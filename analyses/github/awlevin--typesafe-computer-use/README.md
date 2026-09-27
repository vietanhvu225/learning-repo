---
repo: awlevin/typesafe-computer-use
provider: github
canonical_id: github.com/awlevin/typesafe-computer-use
url: https://github.com/awlevin/typesafe-computer-use
aliases:
  - https://github.com/awlevin/typesafe-computer-use.git
  - git@github.com:awlevin/typesafe-computer-use.git
upstream: null
analyzed_at: 2026-09-28
analyzed_commit: 2fc5efaaab692122df23e312fe9ba6e87753b3fc
analysis_version: 1
status: analyzed
adoption: experiment
confidence: high
tags:
  - ai-agents
  - workflow-automation
  - evidence-grounding
  - evals
---

# Phân tích `awlevin/typesafe-computer-use`

## Kết luận ngắn

`typesafe-computer-use` là agent điều khiển desktop và trình duyệt: code biến màn hình thành trạng thái có cấu trúc, TypeSafe chọn một hành động trong tập hữu hạn, còn writer chỉ tạo văn bản tự do hoặc đọc kết quả khi vòng lặp dừng. Đây là một ví dụ tốt về việc thu nhỏ vai trò của model trong workflow AI: tính sự kiện bằng code, giới hạn lựa chọn theo khả năng thực thi, quan sát lại sau mỗi hành động và lưu đủ artifact để phân tích lỗi. [`typesafe_computer_use/decide.py:126-160`, `typesafe_computer_use/decide.py:203-253`, `typesafe_computer_use/runner.py:254-306`, `typesafe_computer_use/runner.py:146-208`]

**Quyết định: `experiment`.** Nên thử các pattern quyết định có cấu trúc, guard trước hành động và replay trên workflow AI nội bộ; chưa nên dùng trực tiếp agent này cho tác vụ thật. Backend trình duyệt hiện kiểm tra `min_confidence` *sau* khi đã thực hiện hành động, trái với desktop backend. [`typesafe_computer_use/browser/runner.py:217-278`, `typesafe_computer_use/browser/runner.py:300-311`, `typesafe_computer_use/runner.py:319-338`]

## Phạm vi và danh tính phiên bản

- Origin Git: `https://github.com/awlevin/typesafe-computer-use`; nhánh checkout: `main`; HEAD: `2fc5efaaab692122df23e312fe9ba6e87753b3fc`. Đây là shallow clone và working tree nguồn sạch khi đọc, xác minh bằng `git remote -v`, `git branch --show-current`, `git rev-parse HEAD`, `git rev-parse --is-shallow-repository` và `git status --porcelain=v1`.
- Commit có ngày `2026-09-25T23:39:32-06:00` theo `git show -s --date=iso-strict`.
- Metadata package ghi phiên bản `0.2.0`, Python `>=3.12`, giấy phép MIT và entry points `clicker`, `clicker-inspect`, `clicker-bench`. Đây là thông tin khai báo của dự án, không phải xác nhận package đã cài hoặc chạy được. [`pyproject.toml:1-10`, `pyproject.toml:43-50`]

## Repo làm gì

CLI `clicker` nhắm tới desktop macOS với screen capture, OCR, accessibility và input thật; tài liệu gọi Windows là experimental và nói rõ adapter chưa được thử trên Windows. Backend browser riêng dùng Chrome DevTools Protocol (CDP), chỉ bật qua `clicker-bench`, dùng profile Chrome tạm. [`README.md:14-29`, `README.md:58-61`, `docs/windows.md:1-5`, `docs/browser-backend.md:1-9`, `typesafe_computer_use/browser/cdp.py:80-88`]

Mục tiêu phù hợp để học ở đây là **kiến trúc điều phối hành động AI**, không phải thay công cụ computer-use hiện tại. Cả hai backend thể hiện cùng một vòng: perception → state và lựa chọn → action → observation mới → stop/review. [`docs/how-a-step-works.md:3-32`, `typesafe_computer_use/browser/runner.py:166-211`, `typesafe_computer_use/browser/runner.py:273-313`]

## Kiến trúc và luồng chính

1. **Desktop perception:** chụp vùng cửa sổ trước, OCR và lấy control từ accessibility tree; cache OCR chỉ đọc lại vùng tile thay đổi khi app/cửa sổ không đổi. Các item được hợp nhất, giữ nguồn OCR/AX và ref để có thể nhấn bằng accessibility. [`typesafe_computer_use/perception.py:76-105`, `typesafe_computer_use/perception.py:135-196`]
2. **Tạo sự kiện trước khi hỏi model:** state gồm goal, thời gian, app, URL, field đang focus, tám hành động gần nhất, các hành động đã thử trên màn hình này và item theo thứ tự đọc; code thêm ngữ cảnh ngày và hàng cho nhãn lặp. [`typesafe_computer_use/decide.py:72-104`, `typesafe_computer_use/decide.py:126-160`]
3. **Quyết định hẹp:** một request TypeSafe hỏi `kind`, `site`, `item` nếu có item và `offscreen` nếu có control ẩn. `Decision.confidence` lấy mức thấp hơn giữa loại hành động và target cho click/press; desktop dừng trước khi hành động nếu dưới ngưỡng. [`typesafe_computer_use/decide.py:163-200`, `typesafe_computer_use/decide.py:203-253`, `typesafe_computer_use/runner.py:319-338`]
4. **Action và phản hồi:** accessibility press được ưu tiên cho control có ref, click tọa độ là fallback. Sau mỗi action, desktop chụp lại để phát hiện màn hình không đổi hoặc lặp; writer chỉ soạn text, URL, hoặc review tại điểm dừng và có thể trả một `focus`/câu hỏi có giới hạn vòng. [`typesafe_computer_use/actions.py:33-66`, `typesafe_computer_use/runner.py:341-385`, `typesafe_computer_use/runner.py:146-208`]
5. **Browser backend:** JS đọc element có thể tương tác trong viewport qua CDP, trả nhãn, tọa độ, trạng thái bị che và dấu hiệu credential. Action set chỉ gồm việc page và writer có thể làm. Sau action, lần quan sát chờ thay đổi cũng trở thành perception của bước kế tiếp. [`typesafe_computer_use/browser/perceive.py:30-103`, `typesafe_computer_use/browser/decide.py:84-115`, `typesafe_computer_use/browser/runner.py:166-211`, `typesafe_computer_use/browser/runner.py:273-278`]

## Observed in code

- **Tách model theo chức năng:** classifier chỉ chọn từ `Choice`; writer trả lời dạng cấu trúc cho text và URL. Code chỉ kiểm tra URL là HTTPS, `netloc` có dấu chấm và không có whitespace và từ chối một số nhãn/giá trị giống credential trước khi gõ trong browser. [`typesafe_computer_use/decide.py:203-253`, `typesafe_computer_use/writer.py:142-179`, `typesafe_computer_use/writer.py:218-278`]
- **Không offer hành động chắc chắn thất bại trong browser:** thiếu field hoặc writer thì bỏ `type_text`; thiếu lịch sử thì bỏ `back`; page không scroll thì bỏ scroll. Test offline kiểm tra các trường hợp này. [`typesafe_computer_use/browser/decide.py:84-115`, `tests/test_browser_offline.py:103-125`]
- **Có guard cho text nhưng mức bảo vệ khác nhau theo backend:** desktop đọc lại giá trị field, gọi TypeSafe `Noul` để verify rồi chỉ phục hồi nếu đúng element vẫn giữ nguyên text vừa gõ; browser chặn password field trước khi hỏi writer và clear field khi verify thấp. [`typesafe_computer_use/actions.py:85-115`, `typesafe_computer_use/actions.py:152-169`, `typesafe_computer_use/browser/runner.py:88-102`, `typesafe_computer_use/browser/runner.py:227-246`]
- **Stop dựa vào quan sát:** desktop so signature app, URL, focus và hàng của từng dòng; cho phép sai khác nhỏ do đồng hồ/OCR. Runner dừng sau ba action không đổi màn hình hoặc hai action lặp tại cùng màn hình. [`typesafe_computer_use/models.py:80-110`, `typesafe_computer_use/runner.py:23-28`, `typesafe_computer_use/runner.py:341-385`]
- **Artifact có thể truy vết:** desktop lưu raw/annotated screenshot, payload, phân bố xác suất, timing và `run.json`; browser lưu state, answers, element list và có hàm dựng lại page từ file để replay quyết định. [`typesafe_computer_use/runner.py:115-132`, `typesafe_computer_use/runner.py:254-302`, `typesafe_computer_use/browser/report.py:50-87`, `typesafe_computer_use/browser/report.py:139-197`]
- **Test/CI tồn tại nhưng không được chạy trong lượt này:** workflow khai báo Ruff + pytest trên macOS, pytest trên Linux và kiểm tra Terraform; test scenario desktop xác nhận low-confidence không click. [`.github/workflows/ci.yaml:8-46`, `tests/test_scenarios.py:437-450`]

## Claimed by project

- README báo chi phí `$0.0002` mỗi quyết định, nhanh hơn và rẻ hơn Claude Opus 5 trong một phép đo trên cùng screenshot/goal; đây là benchmark do dự án cung cấp, không chứng minh hiệu năng đại diện cho nhiều tác vụ hay môi trường. README cũng thừa nhận classifier cần code bổ sung việc parse ngày mà model lớn tự suy ra từ ảnh. [`README.md:31-56`]
- Tài liệu browser công bố DOM perception nhanh hơn OCR `62–221x` trên ba trang và loop p50 `302–380 ms`/bước. Không có benchmark độc lập được chạy trong lượt phân tích này. [`docs/browser-backend.md:17-34`]
- Dự án mô tả OSWorld làm môi trường benchmark có chấm điểm và lưu trajectory; tài liệu nói hai agent dùng observation khác nhau (`screenshot_a11y_tree` và `screenshot`), nên so sánh thời gian/kết quả cần giữ biến này. [`docs/osworld.md:1-7`, `docs/osworld.md:34-44`]
- Dự án tự nhận Beta, có rough edges và hành vi/settings có thể đổi giữa các release 0.x. [`README.md:27-29`]

## Inferences

- **Độ chắc chắn cao:** các pattern state-first và option filtering có thể giảm bước vô ích trong workflow AI khác, vì model chỉ thấy lựa chọn có thể thực thi và được cung cấp sự kiện mà code tính được. Đây là suy luận thiết kế, chưa phải kết quả đo trên `repo-learning`. [`typesafe_computer_use/decide.py:126-160`, `typesafe_computer_use/browser/decide.py:84-115`]
- **Độ chắc chắn trung bình:** log mỗi quyết định với input, lựa chọn và kết quả quan sát sẽ giúp tái hiện lỗi agent nhanh hơn chỉ giữ transcript hội thoại. Code đã persist các artifact đó; lợi ích thực tế phụ thuộc quy trình review và chính sách lưu dữ liệu. [`typesafe_computer_use/runner.py:254-302`, `typesafe_computer_use/browser/report.py:50-87`]
- **Độ chắc chắn trung bình:** confidence chỉ nên là tín hiệu chặn một hành động cụ thể sau khi hiệu chuẩn bằng eval của chính workflow. Repo dùng ngưỡng mặc định `0.4`, nhưng không thấy bằng chứng trong các file đã đọc rằng xác suất này được calibration cho mọi tác vụ desktop/browser. [`typesafe_computer_use/config.py:10-17`, `typesafe_computer_use/decide.py:186-196`, `typesafe_computer_use/browser/runner.py:300-311`]

## Điểm mạnh

1. **Decision contract dễ kiểm tra:** model chọn một action và target từ danh sách hữu hạn; ngày, focus, URL, lịch sử và khả năng thao tác được tính ở code. Điều này làm một bước agent có input/output rõ hơn prompt tự do. [`typesafe_computer_use/decide.py:91-160`, `typesafe_computer_use/browser/decide.py:84-115`]
2. **Observation là chứng cứ của action:** mô tả action chỉ ghi điều đã thử; màn hình tiếp theo quyết định có tiến triển hay không. Signature và artifact khiến stall có thể điều tra. [`typesafe_computer_use/runner.py:23-28`, `typesafe_computer_use/runner.py:341-385`, `typesafe_computer_use/browser/report.py:50-87`]
3. **Escalation có giới hạn:** writer không chọn click; review có `focus` một bước hoặc hỏi user, bị chặn bởi số handoff, câu hỏi và step. [`typesafe_computer_use/runner.py:146-208`, `docs/how-a-step-works.md:189-208`]
4. **Perception phù hợp bề mặt:** OCR+AX cho desktop; DOM cho browser, với hạn chế được tài liệu ghi rõ. [`typesafe_computer_use/perception.py:76-105`, `typesafe_computer_use/browser/perceive.py:1-20`, `docs/browser-backend.md:84-89`]

## Điểm yếu và rủi ro

1. **Browser confidence gate đặt sai thứ tự:** `run_goal()` chọn và thực hiện `click`, `type_text`, `navigate` hoặc action khác ở dòng 217–278; kiểm tra `decision.confidence < min_confidence` chỉ ở dòng 306–308. Một lựa chọn dưới ngưỡng vẫn có thể tác động trang trước khi vòng lặp dừng. Desktop đã gate trước ở `resolve()`. Đây là lý do chính không áp dụng trực tiếp browser loop cho tác vụ có hậu quả. [`typesafe_computer_use/browser/runner.py:217-278`, `typesafe_computer_use/browser/runner.py:300-311`, `typesafe_computer_use/runner.py:319-338`]
2. **Log có thể chứa dữ liệu nhạy cảm:** desktop ghi screenshot, goal, history và payload mỗi bước; history của thao tác gõ bao gồm text đã gõ. Browser loại bỏ giá trị input hiện có khỏi perception, nhưng `detail`/`run.json` của text do writer tạo vẫn chứa chuỗi đó. Cần giới hạn lưu giữ, lọc/redact theo use case và không hiểu tuyên bố “không đọc giá trị field” thành “run folder không bao giờ chứa text nhạy cảm”. [`typesafe_computer_use/browser/perceive.py:63-70`, `typesafe_computer_use/actions.py:152-169`, `typesafe_computer_use/runner.py:115-132`, `typesafe_computer_use/runner.py:254-302`, `typesafe_computer_use/browser/runner.py:238-246`, `typesafe_computer_use/browser/runner.py:315-327`]
3. **Dữ liệu có thể rời máy trước cả bước lưu log:** classifier gửi state gồm screen text/history tới TypeSafe; answer writer nhận screen text và, khi vision bật, cả screenshot. Writer mặc định dùng Anthropic API/model và vision mặc định bật, dù endpoint có thể cấu hình lại. Với desktop hoặc tài khoản nhạy cảm, cần consent, allowlist/redaction trước model call và policy riêng cho endpoint local/cloud; chỉ redact artifact sau đó là chưa đủ. [`typesafe_computer_use/decide.py:240-253`, `typesafe_computer_use/writer.py:344-369`, `typesafe_computer_use/config.py:16-20`, `typesafe_computer_use/config.py:51-80`, `typesafe_computer_use/config.py:91-96`]
4. **Guard URL chỉ là kiểm tra cú pháp tối thiểu:** `valid_url` yêu cầu HTTPS, dấu chấm trong `netloc` và không có whitespace; không ràng buộc domain được phép hay ý định người dùng. Nên thêm policy riêng trước navigation trong workflow có dữ liệu/tài khoản. [`typesafe_computer_use/writer.py:177-179`, `typesafe_computer_use/writer.py:265-278`]
5. **Giới hạn perception:** desktop bỏ sót icon không có text/AX, chỉ chụp màn hình chính; browser bỏ canvas, text trong ảnh, iframe và shadow DOM. [`docs/known-limits.md:1-14`, `docs/browser-backend.md:84-89`]
6. **Chất lượng và tốc độ chưa được tái xác minh:** README đưa phép so sánh một quyết định; Windows được ghi là chưa thử trên Windows. Không nên dùng con số benchmark làm business case trước khi đo trên task và máy đích. [`README.md:42-56`, `docs/windows.md:1-5`]

## Recommendations

| Ý tưởng áp dụng cho workflow AI | Cách thử và chi phí/trade-off |
|---|---|
| **State builder deterministic** | Với mỗi bước agent, tính trước facts như file/commit hiện tại, quyền ghi, trạng thái test và hành động đã thử; chỉ gửi state ngắn cho model. Chi phí là viết/duy trì bộ trích xuất theo domain. [`typesafe_computer_use/decide.py:126-160`] |
| **Action schema và option filtering** | Định nghĩa action mutually exclusive, điều kiện thực thi và target ID; bỏ option không khả dụng trước model call. Cần giữ schema đồng bộ với executor để không tạo “phantom actions”. [`typesafe_computer_use/browser/decide.py:84-115`, `typesafe_computer_use/actions.py:33-48`] |
| **Pre-action gate + post-action witness** | Chặn low confidence, thiếu quyền hoặc sai target *trước* side effect; sau action thu observation mới để xác nhận tiến triển. Thử trước trong task read-only/reversible, tạo eval cho tình huống confidence thấp. [`typesafe_computer_use/runner.py:319-355`, `tests/test_scenarios.py:437-450`] |
| **Step artifact và offline replay** | Lưu state, criteria, lựa chọn, confidence, effect/observation và version của policy cho mỗi bước; redact secret, đặt retention và tránh ghi nguyên screenshot khi không cần. Tốn storage và công bảo vệ dữ liệu, đổi lại lỗi có thể tái hiện. [`typesafe_computer_use/browser/report.py:50-87`, `typesafe_computer_use/browser/report.py:139-197`] |
| **Escalation một bước** | Khi policy dừng, reviewer chỉ đưa một focus hoặc một câu hỏi; giới hạn số vòng. Cần đo tỷ lệ reviewer cứu được task và chi phí model trước khi mở rộng. [`typesafe_computer_use/runner.py:146-208`] |

Thứ tự thử hợp lý: (1) một workflow AI có action giả lập, (2) replay các bước thất bại thành eval, (3) đo số bước vô ích, tỷ lệ hoàn thành và false stop, (4) chỉ sau đó cho phép action thật ở môi trường cô lập. Đây là đề xuất cho `repo-learning`, không phải hành vi có sẵn của dự án.

## Quyết định áp dụng

**`experiment`** cho pattern, **chưa tích hợp package như runtime production**. Cụ thể, áp dụng ý tưởng state deterministic, option filtering, pre-action gate, witness và replay trong một prototype nhỏ; đánh giá bằng task thật của nhóm. Browser loop cần sửa thứ tự confidence gate và bổ sung test low-confidence không gây side effect trước khi cân nhắc tái dùng. Việc không chạy code trong lượt này cũng ngăn kết luận về chất lượng thực tế của OCR, AX, writer và benchmark. [`typesafe_computer_use/browser/runner.py:217-278`, `typesafe_computer_use/browser/runner.py:300-311`, `tests/test_scenarios.py:437-450`]

## Evidence map

| Nhận định | Nguồn |
|---|---|
| Danh tính package, version, entry points | `pyproject.toml:1-10`, `pyproject.toml:43-50` |
| Perception desktop và OCR cache | `typesafe_computer_use/perception.py:76-105`, `typesafe_computer_use/perception.py:135-196` |
| State và TypeSafe Choice | `typesafe_computer_use/decide.py:126-160`, `typesafe_computer_use/decide.py:203-253` |
| Desktop stop trước action | `typesafe_computer_use/runner.py:319-338`, `tests/test_scenarios.py:437-450` |
| Handoff/review | `typesafe_computer_use/runner.py:146-208` |
| Browser option filtering | `typesafe_computer_use/browser/decide.py:84-115`, `tests/test_browser_offline.py:103-125` |
| Browser action trước confidence gate | `typesafe_computer_use/browser/runner.py:217-278`, `typesafe_computer_use/browser/runner.py:300-311` |
| Artifact và replay | `typesafe_computer_use/runner.py:254-302`, `typesafe_computer_use/browser/report.py:50-87`, `typesafe_computer_use/browser/report.py:139-197` |
| Credential guard và URL validation | `typesafe_computer_use/browser/perceive.py:63-70`, `typesafe_computer_use/browser/runner.py:88-102`, `typesafe_computer_use/writer.py:177-179` |
| Benchmark do dự án nêu | `README.md:42-56`, `docs/browser-backend.md:17-34` |

## Hạn chế của phân tích

- Chỉ đọc source, tài liệu, test và Git metadata ở commit đã ghi; không chạy repo, test, benchmark, script, dependency installer hoặc agent trên máy thật.
- Không kiểm tra phiên bản mới hơn HEAD của shallow clone, issue/PR ngoài repo, khả năng calibration thực tế của TypeSafe, hay kết quả OSWorld độc lập.
- CI file cho biết các job được cấu hình, không xác nhận job tại commit này đã pass. [`.github/workflows/ci.yaml:8-46`]
- Cảnh báo browser confidence gate dựa trên thứ tự lệnh đọc trong source; chưa chạy một test để tái hiện side effect.
