# clubSENsational General Induction (Provisional)

Six-module staff induction: **Induction Journey**, **module video**, **Ready for the Quiz**, and **8-question quiz** per module.

## Build

```bash
python3 build_provisional.py
cd dist && python3 -m http.server 8765
```

Open http://localhost:8765/general-induction/

## Vercel

- **Build command:** `python3 build_provisional.py`
- **Output directory:** `dist`

## Module flow

1. Review the six-module journey and confirm understanding
2. Watch the module video (unlocks completion)
3. Open **Ready for the Quiz**
4. Answer all 8 questions and submit (8/8 correct required to pass)

Videos live in `common/assets/videos/module-1.mp4` … `module-6.mp4`.
