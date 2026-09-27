---
repo: chetaslua/jevmeter
provider: github
canonical_id: github.com/chetaslua/jevmeter
url: https://github.com/chetaslua/jevmeter
aliases:
  - https://github.com/chetaslua/jevmeter.git
  - git@github.com:chetaslua/jevmeter.git
upstream: null
analyzed_at: 2026-09-28
analyzed_commit: cbf8e117b5b8835e3294c3a8ee652c7dfa737a9a
analysis_version: 1
status: analyzed
adoption: experiment
confidence: high
tags:
  - evals
  - evidence-grounding
  - video-analysis
  - workflow-automation
---

# Phân tích `chetaslua/jevmeter`

## Kết luận ngắn

`jevmeter` là pipeline Python biến video/URL, có thể kèm transcript, thành một video 16:9 có “đồng hồ” xác suất cho từng câu nói. Luồng chính là transcribe → score từng câu qua TypeSafe Jev → lập timeline/highlight bằng rule cố định → render video. [Nguồn: `README.md`, dòng 200–210, 273–284]

Điểm đáng học cho workflow AI không nằm ở nhãn “BS”, mà ở cách repo thu hẹp một phán đoán chủ quan thành các câu hỏi yes/no nhỏ, có định nghĩa, positive/negative examples và hard near-misses; model chỉ đưa ra probability, còn code deterministic chịu trách nhiệm cache, threshold, aggregation, fairness và artifact cuối. [Nguồn: `jevmeter/presets/debate.json`, dòng 8–119; `jevmeter/score.py`, dòng 27–45; `jevmeter/plan.py`, dòng 27–56]

Nên **experiment**, không adopt nguyên sản phẩm. Bốn pattern đáng thử ngay là: typed micro-decisions, prompt eval có held-out near-misses, cache fingerprint theo model/prompt/input, và wizard/doctor cho workflow nhiều dependency. Không nên coi score là sự thật hoặc suy rộng claim 99% sang hội thoại thực tế.

## Repo làm gì

Repo cung cấp CLI `jevmeter` cho Python 3.9+, dùng Whisper local để lấy word timestamps, gọi TypeSafe System One một lần cho mỗi câu, rồi render overlay/video bằng Pillow và ffmpeg. Package có bốn preset: debate, earnings call, podcast và sales pitch. [Nguồn: `pyproject.toml`, dòng 5–20; `README.md`, dòng 114–135, 200–210]

Người dùng có thể chạy wizard, truyền file hoặc URL, dùng transcript gắn speaker, chọn full video hoặc auto-highlight, và sửa `edl.json` trước khi render lại. `doctor` kiểm tra Python, ffmpeg, speech-to-text backend và API key. [Nguồn: `README.md`, dòng 17–63, 254–284; `jevmeter/cli.py`, dòng 215–237]

## Kiến trúc và luồng chính

```text
video / URL + transcript tùy chọn
             ↓
 Whisper word timestamps + align transcript
             ↓
 sentence state: speaker + context + history + answer-so-far
             ↓
 TypeSafe Jev: nhiều câu hỏi xác suất cho mỗi sentence
             ↓
 deterministic thresholds + per-speaker summary + highlight EDL
             ↓
 Pillow/ffmpeg render + audio + video output
```

### 1. Transcribe và align

Nếu có transcript, text trong transcript là nguồn chính còn Whisper cung cấp timestamp; `SequenceMatcher` align token và nội suy những khoảng có coverage thấp. Không có transcript thì Whisper text được tách thành câu và coi là một speaker. [Nguồn: `jevmeter/transcribe.py`, dòng 1–7, 69–102, 105–133]

### 2. Biến context thành typed decision

Mỗi câu được đóng gói cùng speaker, lượt context gần nhất, tối đa 25 câu trước của cùng speaker và phần answer hiện tại. Mỗi preset question trở thành một `noul` có instructions và optional criteria. [Nguồn: `jevmeter/score.py`, dòng 27–68]

Preset debate minh họa prompt contract khá tốt: mỗi câu hỏi nêu field cần phán đoán, định nghĩa rõ true/false và cung cấp near-miss như “lời hứa có con số” nhưng không phải factual claim, hoặc “thank you” trước một câu trả lời trực tiếp không phải né tránh. [Nguồn: `jevmeter/presets/debate.json`, dòng 9–51, 98–117]

### 3. Score có cache và resumability

Score cache được fingerprint theo model, context label và toàn bộ question contract. Nếu fingerprint đổi, file cũ được giữ sang tên; kết quả mới được append và flush từng dòng nên rerun chỉ gọi lại những sentence chưa thành công. Request dùng thread-local keep-alive session, chạy song song và retry tối đa sáu lần. [Nguồn: `jevmeter/score.py`, dòng 71–95, 97–133]

### 4. Model judge, code quyết định

Code chọn tối đa hai speaker chính theo lượng từ; threshold mặc định là percentile 98 với floor 0.5; index là trung bình các question có `index: true`. Auto-highlight xếp hạng các đoạn 10–15.5 giây, giữ khoảng cách giữa clip và xen kẽ speaker để đối xử đối xứng. [Nguồn: `jevmeter/plan.py`, dòng 9–24, 27–56, 59–101]

Đây là boundary đáng học: model xử lý semantic judgement; phép tổng hợp, selection policy và output structure do code kiểm soát và có thể kiểm tra.

## Observed in code

- Package nhỏ, entry point rõ, dependency runtime giới hạn; Whisper backend là optional extra theo platform. [Nguồn: `pyproject.toml`, dòng 5–26]
- Scoring gửi sentence cùng context, lịch sử và answer-so-far đến API mặc định `https://api.typesafe.ai/v1/systemone`; video được xử lý local nhưng text/context không hoàn toàn local. [Nguồn: `jevmeter/score.py`, dòng 15–35, 97–109]
- API key được tìm theo env → `.env` ở current directory → user config; file user config được tạo với quyền `600`. [Nguồn: `jevmeter/config.py`, dòng 1–12, 15–50]
- CI scan secret, compile package, gọi `--help`, parse preset JSON và smoke-test transcript parsing. Không thấy unit/integration test suite riêng trong file tracked tại commit này. [Nguồn: `.github/workflows/ci.yml`, dòng 1–20]
- Secret scanner dùng regex trên tracked/untracked text file và có thể cài optional pre-commit hook. Đây là defense-in-depth hữu ích nhưng không thay thế secret scanner chuyên dụng. [Nguồn: `scripts/check_secrets.py`, dòng 1–21, 24–45]
- URL được tải bằng `yt-dlp`; README và docstring nhắc người dùng chỉ xử lý footage có quyền sử dụng. [Nguồn: `jevmeter/cli.py`, dòng 48–65; `README.md`, dòng 286–294]

## Claimed by project

- README nói shipped presets đạt 99% accuracy và AUC 1.00 trên 200 held-out sentences. File kết quả mô tả test set gồm 5 yes + 5 no cho mỗi question, ít nhất ba hard near-misses trong mỗi nhóm no; dev set 135 câu được dùng để viết criteria. [Nguồn: `README.md`, dòng 127–135; `eval/RESULTS.md`, dòng 3–13]
- Đây là số do dự án công bố; lượt phân tích này không có API key và không chạy benchmark để xác minh độc lập.
- Kết quả chi tiết vẫn có question chỉ đạt 90% accuracy, và chính tác giả lưu ý dataset nhỏ không chứng minh preset đúng trên mọi video; speech thực tế phức tạp hơn. [Nguồn: `eval/RESULTS.md`, dòng 22–45, 47–56]
- README công bố chi phí, latency và battle statistics cho một lần chạy debate; các số này chưa được tái lập trong lượt phân tích. [Nguồn: `README.md`, dòng 93–110]

## Inferences

### Typed micro-decisions là primitive hữu ích cho agent

Thay vì hỏi model “repo này có tốt không?”, workflow có thể hỏi nhiều câu hẹp hơn: có test tự động không, claim benchmark có reproducible không, mutation nào cần approval, output có portable không, recommendation nào được source support. Mỗi câu cần schema, criteria và counterexample. Sau đó code tổng hợp thành adoption decision. Đây là suy luận thiết kế từ question contract và deterministic planner của repo.

### Hard negatives có giá trị hơn prompt dài chung chung

Mức tăng được báo cáo từ 94.5% lên 99% gắn với field naming, true/false criteria và near-misses. Dù dataset nhỏ, cách thiết kế eval này hợp lý hơn chỉ chỉnh prompt theo cảm giác: lưu những case dễ nhầm, tách dev/test và đo lại sau mỗi thay đổi. [Nguồn: `eval/RESULTS.md`, dòng 5–20]

### Artifact pipeline phù hợp công việc dài hạn

Append-only score file, fingerprint và EDL editable cho phép dừng/chạy lại mà không trả chi phí toàn bộ. Cùng pattern có thể áp dụng cho repo-learning: cache inventory/facts theo commit + analysis schema version; chỉ regenerate phần bị ảnh hưởng.

## Điểm mạnh

1. **Prompt contract cụ thể:** field, definition, true/false criteria và near-miss nằm trong JSON, dễ review và version-control. [Nguồn: `jevmeter/presets/debate.json`, dòng 8–119]
2. **Separation of concerns:** model chấm semantic probability; code thực hiện aggregation, threshold, symmetry và render.
3. **Resumable có điều kiện:** prompt/model đổi thì invalidate score; lỗi giữa chừng không mất kết quả thành công. Resume chỉ an toàn khi input/state không đổi vì fingerprint hiện chưa bao gồm nội dung sentence. [Nguồn: `jevmeter/score.py`, dòng 71–95, 119–133]
4. **Evaluation artifact trong repo:** dev/test data, runner, before/after metrics và limitations được lưu cùng code. [Nguồn: `eval/RESULTS.md`, dòng 1–56]
5. **Beginner UX tốt:** wizard, setup và doctor bao quanh pipeline vốn có nhiều dependency. [Nguồn: `README.md`, dòng 17–63]
6. **Responsible-use note rõ:** probabilities không phải verdict/fact-check; rule phải áp dụng giống nhau cho các speaker. [Nguồn: `README.md`, dòng 286–294]

## Điểm yếu và rủi ro

### 1. Nhãn chủ quan dễ tạo cảm giác khách quan giả

Một số question như evasive, emotional appeal hay unsupported phụ thuộc context và chuẩn mực. UI xác suất, threshold và scoreboard có thể khiến người xem hiểu thành fact-check dù model không kiểm chứng sự thật. README đã cảnh báo, nhưng người tái sử dụng output vẫn phải giữ disclaimer và cho phép audit criteria.

### 2. Privacy boundary cần nói rõ

Video/audio được transcribe local, nhưng sentence cùng context và lịch sử được gửi tới TypeSafe API. Transcript cuộc họp, earnings call nội bộ hoặc video chưa công bố có thể chứa dữ liệu nhạy cảm. [Nguồn: `jevmeter/score.py`, dòng 27–35, 97–109]

### 3. Transcript và score cache có thể stale

`whisper_words.json` được tái sử dụng chỉ vì file tồn tại; cache không fingerprint video, model, language, start/end hoặc transcript. Đổi input/config nhưng giữ cùng work directory có thể dùng nhầm timestamps cũ. [Nguồn: `jevmeter/transcribe.py`, dòng 136–156]

Score cache fingerprint model, context label và questions nhưng không fingerprint sentence/state; kết quả cũ được map lại chỉ bằng ID đánh từ 0. Sửa transcript hoặc đổi video mà giữ work directory có thể gán score cũ cho câu mới. Resume chỉ an toàn khi input/state không đổi. [Nguồn: `jevmeter/score.py`, dòng 71–94; `jevmeter/transcribe.py`, dòng 154–156]

Nếu áp dụng pattern, mọi expensive stage cần content/config fingerprint riêng, bao gồm hash của input hoặc state thực tế.

### 4. Validation còn thiên về smoke test

CI compile code, parse JSON và test một assertion nhỏ trên mock transcript, nhưng không thấy test cho retry/cache invalidation, alignment edge case, highlight fairness, render hoặc destructive work-directory behavior. [Nguồn: `.github/workflows/ci.yml`, dòng 11–20]

### 5. Work directory là vùng mutation

`render_parts()` xóa mọi file có prefix `part_` trong work directory trước khi render. Bình thường work dir là folder riêng `<video>.jevmeter`, nhưng `--work` cho phép user trỏ tới folder khác. Cần validate sentinel/ownership trước cleanup nếu harden sản phẩm. [Nguồn: `jevmeter/cli.py`, dòng 79–80, 127–130]

### 6. Benchmark nhỏ và hand-labelled

200 test sentences, chỉ 10 case/question, chưa đại diện accent, transcription error, multi-turn ambiguity, domain shift hoặc long context. AUC hoàn hảo trên tập này là tín hiệu tốt cho prompt iteration, không phải bằng chứng tổng quát về correctness. [Nguồn: `eval/RESULTS.md`, dòng 3–13, 55–56]

## Recommendations

### P0 — áp dụng vào workflow phân tích repo

1. **Tạo rubric dạng câu hỏi nhỏ:** mỗi analysis pass trả structured answer cho provenance, tests, security, privacy, caching, portability, maintenance và adoption.
2. **Viết cả criteria true/false:** bổ sung near-miss, ví dụ “có thư mục test” không đồng nghĩa “test được chạy trong CI”, “README claim” không đồng nghĩa “observed in code”.
3. **Để code tổng hợp:** validator/index generator quyết định duplicate, missing evidence và status; LLM không tự sửa registry theo prose tùy ý.
4. **Fingerprint từng stage:** canonical URL + commit + analysis schema + rubric version. Khi rubric đổi, giữ analysis cũ trong Git và regenerate có chủ đích.
5. **Append/checkpoint công việc dài:** facts/evidence thu được nên ghi bền vững trước synthesis để session lỗi không phải đọc lại toàn bộ repo.

### P1 — xây eval sau khi có 5–10 bài

Tạo dev/test cases từ lỗi thật:

- marketing claim bị ghi thành fact;
- repo có tests nhưng CI không chạy;
- HTTPS/SSH/`.git` cùng trỏ một canonical repo;
- cache phải invalid khi commit/rubric đổi;
- report có recommendation nhưng thiếu evidence;
- đường dẫn tuyệt đối làm report không portable;
- sensitive data xuất hiện trong report.

Mỗi lần chỉnh template/skill, chạy held-out cases và công bố cả failure, không chỉ overall score.

### P2 — học UX, không sao chép domain label

Thêm `doctor`/preflight cho Git, authentication, registry validity, index freshness và writable workspace. Giữ tên rubric trung tính (`evidence coverage`, `adoption readiness`) thay vì nhãn gây tranh cãi như “BS index”.

## Quyết định áp dụng

| Cơ chế | Quyết định | Lý do |
|---|---|---|
| Typed micro-decisions + criteria | **Adopt now** | Giảm ambiguity, dễ review và eval |
| Deterministic aggregation sau model judgement | **Adopt now** | Kết quả ổn định và audit được |
| Fingerprinted resumable cache | **Adopt now** | Giảm chi phí và tránh trộn kết quả khác version |
| Held-out hard-near-miss eval | **Experiment** | Cần tích lũy case thật trước khi benchmark có ý nghĩa |
| Wizard/doctor/preflight | **Experiment** | Có ích khi pipeline clone/analyze/push bắt đầu phức tạp |
| Dùng score như verdict/fact-check | **Reject** | Model probability không chứng minh sự thật |
| Gửi transcript nhạy cảm sang API mặc định | **Reject/opt-in** | Cần consent và data policy rõ |

Quyết định chung cho repo: **experiment**. Học cơ chế prompt/eval/cache/orchestration; không đưa domain-specific judgement hoặc claim benchmark vào workflow như một chuẩn đã được xác minh.

## Evidence map

| Nhận định | Nguồn |
|---|---|
| Product và pipeline | `README.md:200–210`, `README.md:273–284` |
| Typed question contract | `jevmeter/presets/debate.json:8–119`, `jevmeter/score.py:27–45` |
| Context cho mỗi sentence | `jevmeter/score.py:48–68` |
| Cache/resume/retry | `jevmeter/score.py:71–133` |
| Deterministic threshold/summary | `jevmeter/plan.py:27–56` |
| Highlight symmetry | `jevmeter/plan.py:59–101` |
| Transcript alignment/cache | `jevmeter/transcribe.py:69–102`, `jevmeter/transcribe.py:136–156` |
| Eval claims và limitations | `eval/RESULTS.md:3–20`, `eval/RESULTS.md:22–56` |
| CI coverage | `.github/workflows/ci.yml:1–20` |
| Key handling | `jevmeter/config.py:1–12`, `jevmeter/config.py:38–50` |
| Responsible use | `README.md:286–294` |

## Hạn chế của phân tích

- Chỉ đọc source, tài liệu và Git metadata tại commit đã ghi; không chạy package, installer, API call, benchmark hay render.
- Không đánh giá TypeSafe Jev model độc lập và không xác minh các số accuracy/cost/latency của dự án.
- Không thử video thật nên chưa đo chất lượng Whisper alignment, speaker attribution, output video hoặc hành vi khi network gián đoạn.
- Báo cáo mô tả shallow checkout của `main`; không phân tích lịch sử phát triển ngoài commit hiện tại.
