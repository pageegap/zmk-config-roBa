"""Record exact revisions of the active, cloned West dependencies only.

Older West versions try to freeze inactive optional projects too, although
`west update` intentionally leaves those uncloned. No extra clones are needed.
"""
import sys
import yaml
from west.manifest import Manifest
manifest = Manifest.from_topdir()
projects = []
for project in manifest.projects[1:]:
    if not manifest.is_active(project):
        continue
    if not project.is_cloned():
        raise RuntimeError(f'Active dependency is not cloned: {project.name}')
    entry = project.as_dict()
    entry['revision'] = project.sha('HEAD')
    projects.append(entry)
yaml.safe_dump({'manifest': {'projects': projects, 'self': {'path': 'config'}}}, sys.stdout, sort_keys=False)
