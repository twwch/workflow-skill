#!/usr/bin/env python3
"""
coze.cn workflow import zip 打包工具。

命名契约（通过字节级实验验证）：
    <zip>
    └── Workflow-<NAME>-draft-<DIGITS>/
        ├── MANIFEST.yml
        └── workflow/
            └── <NAME>-draft.yaml

zip 字节格式必须模仿 Go archive/zip 默认流式输出：
  - 只含文件条目，不含目录条目
  - MANIFEST.yml 在前，yaml 在后
  - local header flags = 0x08（bit 3, data descriptor）
  - local + CD 的 time/date 全 0
  - CD 的 vmade = 20 (DOS), external_attr = 0

用法：
    from build_coze_zip import pack_workflow
    pack_workflow(
        name="my_workflow",
        workflow_id="7585079438426599000",
        workflow_yaml_body="...yaml content...",
        desc="workflow 描述",
        out_path="Workflow-my_workflow-draft-0001.zip",
    )
"""
import io
import re
import struct
import sys
import zipfile
from pathlib import Path


class _NoSeekWriter:
    def __init__(self, f):
        self._f = f
    def write(self, b):
        return self._f.write(b)
    def flush(self):
        return self._f.flush()


def _patch_bytes(data: bytes) -> bytes:
    buf = bytearray(data)
    off = 0
    while True:
        idx = buf.find(b'PK\x03\x04', off)
        if idx == -1: break
        struct.pack_into('<HH', buf, idx + 10, 0, 0)
        fnlen = struct.unpack_from('<H', buf, idx + 26)[0]
        exlen = struct.unpack_from('<H', buf, idx + 28)[0]
        off = idx + 30 + fnlen + exlen
    off = 0
    while True:
        idx = buf.find(b'PK\x01\x02', off)
        if idx == -1: break
        struct.pack_into('<H', buf, idx + 4, 20)
        struct.pack_into('<HH', buf, idx + 12, 0, 0)
        struct.pack_into('<I', buf, idx + 38, 0)
        fnlen = struct.unpack_from('<H', buf, idx + 28)[0]
        exlen = struct.unpack_from('<H', buf, idx + 30)[0]
        cmlen = struct.unpack_from('<H', buf, idx + 32)[0]
        off = idx + 46 + fnlen + exlen + cmlen
    return bytes(buf)


def _raw_pack(root_name: str, files: list, out_path: str):
    bio = io.BytesIO()
    wrapper = _NoSeekWriter(bio)
    epoch = (1980, 1, 1, 0, 0, 0)
    with zipfile.ZipFile(wrapper, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel, content in files:
            zi = zipfile.ZipInfo(f'{root_name}/{rel}', date_time=epoch)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, content)
    patched = _patch_bytes(bio.getvalue())
    with open(out_path, 'wb') as f:
        f.write(patched)


_NAME_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')


def pack_workflow(*, name: str, workflow_id: str, workflow_yaml_body: str,
                  desc: str = '', out_path: str, draft_suffix: str = '0001',
                  icon: str = 'plugin_icon/workflow.png'):
    if not _NAME_RE.match(name):
        raise ValueError(f'invalid name {name!r}')
    if not workflow_id.isdigit() or not (15 <= len(workflow_id) <= 20):
        raise ValueError(f'invalid workflow_id {workflow_id!r}')
    if f'name: {name}' not in workflow_yaml_body:
        raise ValueError(f'workflow_yaml_body must contain `name: {name}`')

    root = f'Workflow-{name}-draft-{draft_suffix}'
    yaml_filename = f'{name}-draft.yaml'
    manifest = (
        'type: Workflow\n'
        'version: 1.0.0\n'
        'main:\n'
        f'    id: {workflow_id}\n'
        f'    name: {name}\n'
        f'    desc: {desc}\n'
        f'    icon: {icon}\n'
        '    version: ""\n'
        '    flowMode: 0\n'
        '    commitId: ""\n'
        'sub: []\n'
    )
    _raw_pack(root, [
        ('MANIFEST.yml', manifest),
        (f'workflow/{yaml_filename}', workflow_yaml_body),
    ], out_path)


if __name__ == '__main__':
    src = Path(sys.argv[1])
    out = sys.argv[2]
    manifest = (src / 'MANIFEST.yml').read_text()
    wf_dir = src / 'workflow'
    yaml_files = list(wf_dir.glob('*.yaml'))
    assert len(yaml_files) == 1
    wf_file = yaml_files[0]
    _raw_pack(src.name, [
        ('MANIFEST.yml', manifest),
        (f'workflow/{wf_file.name}', wf_file.read_text()),
    ], out)
    print(f'OK -> {out}')
