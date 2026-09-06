from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = sorted(path for path in ROOT.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.name != 'SBOM.spdx.json')
payload = {
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "DIKWP-ESSENCE-OMEGA-OS-v1.0.0",
  "documentNamespace": "https://example.org/spdx/dikwp-essence-omega-os-v1.0.0",
  "creationInfo": {"created": "2026-09-05T00:00:00Z", "creators": ["Tool: DIKWP-ESSENCE-OMEGA-OS build"]},
  "packages": [{
    "name": "DIKWP-ESSENCE-OMEGA-OS",
    "SPDXID": "SPDXRef-Package",
    "versionInfo": "1.0.0",
    "downloadLocation": "NOASSERTION",
    "filesAnalyzed": False,
    "licenseConcluded": "AGPL-3.0-or-later",
    "licenseDeclared": "AGPL-3.0-or-later",
    "copyrightText": "Copyright (c) 2026 Yucong Duan",
    "externalRefs": []
  }],
  "relationships": [{"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": "SPDXRef-Package"}],
  "annotations": [{"annotationType": "OTHER", "annotator": "Tool: build_sbom.py", "annotationDate": "2026-09-05T00:00:00Z", "comment": f"Reference source tree contains {len(files)} files and has zero runtime third-party Python dependencies."}]
}
(ROOT/'SBOM.spdx.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(ROOT/'SBOM.spdx.json')
