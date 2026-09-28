---
repo: thruwire/foreman
provider: github
canonical_id: github.com/thruwire/foreman
url: https://github.com/thruwire/foreman
aliases:
  - https://github.com/thruwire/foreman.git
  - git@github.com:thruwire/foreman.git
upstream: null
analyzed_at: 2026-09-29
analyzed_commit: 01dd0f1982a1c2d0d71663c1d3851badcce95d6e
analysis_version: 1
status: analyzed
adoption: experiment
confidence: medium
tags:
  - ai-agents
  - workflow-automation
  - evals
  - evidence-grounding
---

# Phân tích `thruwire/foreman`

## Kết luận ngắn

Foreman là bộ giám sát agent viết mã: worker tiếp tục làm việc trong khi vòng giám sát gom bằng chứng, hỏi model các câu kiểm tra có tên và dùng Python chọn hành động. Mẫu đáng thử cho workflow AI-assisted engineering là **quan sát có giới hạn → đánh giá ngữ nghĩa → policy xác định → sự kiện có thể kiểm tra lại**. Chọn **`experiment`** với một luồng nhỏ, có người quyết định trước các hành động quan trọng; chưa dùng Foreman nguyên trạng để điều phối công việc nhạy cảm. `src/foreman/runtime.py:369-430`, `src/foreman/policy.py:39-101`, `src/foreman/models/events.py:11-44`, `README.md:465-476`

## Phạm vi và danh tính phiên bản

- Origin `https://github.com/thruwire/foreman.git`, branch `main`, HEAD `01dd0f1982a1c2d0d71663c1d3851badcce95d6e`; checkout shallow và working tree sạch tại thời điểm phân tích. Đã kiểm tra bằng `git remote -v`, `git branch --show-current`, `git rev-parse HEAD`, `git rev-parse --is-shallow-repository`, `git status --short`.
- Đây là package Python `foreman-core` 0.4.1, yêu cầu Python >=3.11, phụ thuộc Pydantic và TypeSafe SDK, có CLI `foreman`. `pyproject.toml:5-11`, `pyproject.toml:25-42`

Mọi dẫn chiếu `path:line-line` bên dưới tương đối với root của checkout tại HEAD nêu trên.

## Repo làm gì

Một job trên repository được giao cho worker viết mã; vòng giám sát đọc output, trạng thái Git, kết quả kiểm tra và lịch sử, rồi có thể tiếp tục, hướng dẫn, dừng, thử lại, mở lượt verifier, kết thúc hoặc báo cần người. Backend mặc định là Codex App Server; mã cũng có các backend Codex exec, OpenCode và Hermes. `src/foreman/runtime.py:160-175`, `src/foreman/models/events.py:36-44`, `README.md:107-140`, `README.md:142-157`

## Kiến trúc và luồng chính

```text
Job → routing trách nhiệm → worker viết mã
                         ↘ output / Git / test / event
                           observation có giới hạn
                         → Jev trả điểm cho từng check
                         → trách nhiệm đề xuất directive
                         → policy chọn một directive
                         → runtime tác động lên worker và lưu state/event
```

Routing chọn trách nhiệm trước khi chạy worker; watcher gom sự kiện liên tiếp, bỏ qua debounce ở ranh giới lifecycle và đánh giá định kỳ cả khi worker yên lặng. Mỗi check chọn nhóm bằng chứng gửi tới Jev; các check cùng nhóm được gộp một request. `src/foreman/runtime.py:133-158`, `src/foreman/runtime.py:508-566`, `src/foreman/observation.py:64-101`, `src/foreman/foreman/jev.py:112-144`

## Observed in code

1. `FactoryState` ghi job, trạng thái, worker, routing, kết quả đánh giá, lịch sử can thiệp, verifier, lỗi và số lần retry. Enum can thiệp chỉ có tám hành động; model không trực tiếp gọi tool của worker. `src/foreman/models/state.py:45-79`, `src/foreman/models/events.py:36-57`
2. Jev trả điểm số cho các check có tên. Adapter bác câu trả lời thiếu, không phải số hoặc không hữu hạn, rồi chặn điểm vào [0,1]. Trách nhiệm đề xuất directive; policy chọn theo priority và confidence, áp trần iteration, worker và retry. `src/foreman/foreman/jev.py:15-35`, `src/foreman/responsibilities/base.py:10-31`, `src/foreman/policy.py:39-101`
3. Check `needs_human` đạt ngưỡng 0,80 sẽ đề xuất `ESCALATE` ưu tiên 1.000; runtime dừng worker và đặt trạng thái `ESCALATED`. Đây là đường dừng/bàn giao, không thấy giao thức phê duyệt rồi tiếp tục cùng run trong CLI được đọc. Codex App Server worker được khởi tạo với `approvalPolicy: "never"`. `src/foreman/responsibilities/definitions/core.human-escalation.toml:4-8`, `src/foreman/responsibilities/builtin.py:116-138`, `src/foreman/runtime.py:496-506`, `src/foreman/workers/codex_app_server.py:309-318`, `src/foreman/cli.py:269-270`, `src/foreman/cli.py:410-411`, `src/foreman/cli.py:499-500`
4. Khi worker còn chạy, warning drift/stuck/off-track có thể steer một lần, đợi grace period rồi dừng; backend không có kênh steer đi thẳng tới dừng. Sau worker, policy chỉ mở một lượt verifier nếu điểm đạt ngưỡng và `verification_started` chưa bật; hoàn thành đòi điểm requirements, test và ready-to-finish vượt ngưỡng cùng điều kiện verification đã giải quyết. `src/foreman/responsibilities/builtin.py:73-113`, `src/foreman/responsibilities/builtin.py:248-294`, `src/foreman/responsibilities/builtin.py:311-330`, `src/foreman/workers/codex.py:169-172`
5. Observation lấy Git status, diff, tên file thay đổi, output tail, AGENTS.md ở root, kết quả test và event gần đây. Giới hạn mặc định gồm diff 20.000 ký tự, output 12.000, 3 file untracked/4.096 byte. Bộ lọc untracked bỏ symlink, file nhị phân và tên trông nhạy cảm; đây là heuristic chỉ cho nội dung untracked, không phải cơ chế che dữ liệu trong Git diff hoặc stdout. `src/foreman/observation.py:17-48`, `src/foreman/observation.py:176-192`, `src/foreman/observation.py:243-295`, `src/foreman/observation.py:336-413`, `src/foreman/config.py:75-81`
6. `RunStore` lưu `state.json` bằng file tạm + fsync + replace và nối `events.jsonl` với fsync; loader xác thực schema và chuyển đổi state cũ. CLI có lệnh `runs`/`inspect`; `run()` tạo state/run mới. Vì vậy chứng cứ xác nhận khả năng đọc lại và kiểm tra lịch sử, chưa xác nhận tự nối lại worker sau crash. `src/foreman/persistence.py:19-37`, `src/foreman/persistence.py:67-98`, `src/foreman/persistence.py:100-151`, `src/foreman/runtime.py:103-115`, `src/foreman/runtime.py:544-566`, `src/foreman/cli.py:410-411`, `src/foreman/cli.py:499-500`
7. Có test nguồn cho ưu tiên human escalation, quan sát worker đang chạy, ghi state/worker, trích nội dung file untracked và thu command evidence trước khi đánh giá sau worker. Các test này chỉ được đọc, chưa được thực thi trong lượt phân tích. `tests/test_policy.py:57-68`, `tests/test_runtime.py:43-71`, `tests/test_persistence.py:14-30`, `tests/test_untracked_evidence.py:149-186`, `tests/test_integration.py:251-287`

## Claimed by project

- Dự án gọi đây là hai vòng lặp đồng thời và nói worker không phải chờ supervisor mới tiếp tục; code watcher và worker task phù hợp với thiết kế, nhưng chưa đo latency hay lợi ích thực tế. `README.md:70-96`, `src/foreman/runtime.py:508-566`
- README nói demo và suite offline chứng minh các thuộc tính phần mềm; tài liệu riêng giới hạn kết luận ở tính khả thi kiến trúc, không chứng minh chất lượng Jev, hiệu quả, an toàn hoặc độ bền production. Chưa chạy demo/test nên các tuyên bố thực nghiệm vẫn chưa được xác minh ở checkout này. `README.md:351-361`, `README.md:435-444`, `docs/what-foreman-proves.md:1-22`, `docs/what-foreman-proves.md:36-47`
- README mô tả `state.json` có đủ typed state để “recover a run”; quan sát mã và CLI ở trên chỉ xác minh load/inspect, chưa thấy lệnh resume worker sau crash. `README.md:385-404`, `src/foreman/persistence.py:86-98`, `src/foreman/cli.py:410-411`, `src/foreman/cli.py:499-500`

## Inferences

- **Tin cậy cao:** ranh giới model chấm check / code quyết định hành động giúp quyết định kiểm tra được và giữ giới hạn tài nguyên ở code. Điều này không tự chứng minh điểm số đúng hoặc policy an toàn. `src/foreman/foreman/jev.py:15-35`, `src/foreman/policy.py:39-101`, `docs/what-foreman-proves.md:36-46`
- **Tin cậy vừa:** event timeline cùng proposed/selected directive có thể hỗ trợ đánh nhãn false positive/negative và replay policy cho eval workflow. Repository chưa cung cấp benchmark đại diện hay kết quả calibration. `src/foreman/models/result.py:12-20`, `src/foreman/runtime.py:410-428`, `docs/what-foreman-proves.md:24-46`
- **Tin cậy cao:** local run không phải vùng cách ly task. Worker làm trong repository được cấp và OpenCode dùng `--auto`; giám sát ngữ nghĩa có thể can thiệp sau khi một hành động đã xảy ra. `src/foreman/workers/codex.py:61-73`, `src/foreman/workers/opencode.py:13-22`, `src/foreman/runtime.py:508-542`, `SECURITY.md:20-21`

## Điểm mạnh

- Event và state có schema, lưu cả đề xuất lẫn lựa chọn cuối; hữu ích để truy nguyên tại sao supervisor can thiệp. `src/foreman/models/events.py:47-72`, `src/foreman/models/result.py:12-20`, `src/foreman/runtime.py:410-428`
- Check có danh sách evidence riêng, observation có ngân sách; giảm context lặp lại và cho phép so sánh check theo nguồn. `src/foreman/responsibilities/base.py:10-31`, `src/foreman/observation.py:64-101`, `src/foreman/foreman/jev.py:112-144`
- Timeout, retry, số worker, iteration và lỗi assessment liên tiếp được chặn bằng code; lỗi Jev tạm thời cho worker chạy tiếp đến ngưỡng rồi escalates. `src/foreman/config.py:53-81`, `src/foreman/policy.py:43-99`, `src/foreman/runtime.py:378-408`

## Điểm yếu và rủi ro

- Điểm số và ngưỡng mặc định chưa được hiệu chuẩn cho công việc thực. Sai dương có thể dừng worker hữu ích; sai âm có thể để worker tiếp tục sai. `src/foreman/responsibilities/definitions/core.human-escalation.toml:4-8`, `README.md:465-476`, `docs/what-foreman-proves.md:24-46`
- Bằng chứng đưa ra ngoài qua Jev gồm job, output, diff và có thể là nội dung untracked/AGENTS.md; tên file nhạy cảm chỉ được lọc ở nhánh untracked. State/event local cũng lưu job, output và quyết định. Cần chính sách dữ liệu riêng trước khi dùng với repo có bí mật. `src/foreman/observation.py:64-101`, `src/foreman/observation.py:176-192`, `src/foreman/observation.py:365-413`, `src/foreman/foreman/jev.py:116-131`, `src/foreman/models/state.py:45-75`
- Worker không có worktree/container cách ly do Foreman tạo; output từ command evidence kế thừa quyền và môi trường local. Codex App Server đặt `approvalPolicy: "never"`; cơ chế `needs_human` chỉ dừng sau assessment, không phải chốt phê duyệt trước mỗi hành động. `src/foreman/workers/codex_app_server.py:309-318`, `src/foreman/evidence.py:154-205`, `src/foreman/responsibilities/builtin.py:125-138`, `README.md:446-476`
- `git diff` thường không cho thấy staged diff; snapshot giới hạn có thể bỏ phần đầu output/diff và chỉ lấy vài file untracked. Kết luận “tests sufficient” vì vậy phụ thuộc chất lượng và độ đầy đủ của evidence. `src/foreman/observation.py:104-107`, `src/foreman/observation.py:259-295`, `src/foreman/observation.py:346-355`, `src/foreman/config.py:75-81`

## Recommendations

1. **Thử supervisor chỉ ghi nhận trong một workflow nhỏ** (chi phí vừa): chụp job, trạng thái, test, diff và quyết định đề xuất; người vận hành duyệt trước stop/retry/finish. Đo false positive/negative và latency trước khi cho policy tác động tự động. Cơ sở: `src/foreman/runtime.py:369-430`, `src/foreman/policy.py:39-101`, `docs/what-foreman-proves.md:24-46`.
2. **Tách nguồn evidence theo check** (chi phí thấp-vừa): check completion lấy requirements/test/diff; check drift lấy AGENTS.md; ghi provenance và giới hạn context. Thêm kiểm tra staged/untracked đầy đủ và chính sách lọc bí mật trước khi gửi model. Cơ sở: `src/foreman/evidence.py:20-43`, `src/foreman/observation.py:64-101`, `src/foreman/observation.py:346-355`.
3. **Xây eval bằng event timeline** (chi phí vừa-cao): dùng tập job có nhãn kết quả, replay các điểm/threshold, đo can thiệp sớm/sai, chi phí, thời gian và chất lượng verifier. Không lấy test unit của dự án làm bằng chứng hiệu quả production. Cơ sở: `src/foreman/persistence.py:124-151`, `tests/test_policy.py:57-68`, `docs/what-foreman-proves.md:24-47`.
4. **Đặt ranh giới vận hành trước khi thử worker thật** (chi phí vừa): worktree/container riêng, quyền tool rõ ràng, approval cho hành động quan trọng, cơ chế resume tường minh sau crash, retention/redaction state và event. Foreman hiện mới có local persistence và giám sát hậu kiểm. Cơ sở: `src/foreman/workers/codex_app_server.py:309-318`, `src/foreman/persistence.py:67-151`, `SECURITY.md:20-21`, `README.md:465-476`.

## Quyết định áp dụng

**`experiment`**. Áp dụng ý tưởng supervisor quan sát có giới hạn, check có tên, policy xác định và event audit vào một prototype đo được. Chưa triển khai Foreman nguyên trạng trên repository nhạy cảm; chỉ nâng mức áp dụng khi có isolation, approval trước hành động rủi ro và eval chứng minh chất lượng điểm số/can thiệp. `src/foreman/observation.py:17-48`, `src/foreman/policy.py:39-101`, `SECURITY.md:20-21`, `docs/what-foreman-proves.md:36-47`

## Evidence map

| Nhận định | Nguồn |
|---|---|
| State và hành động | `src/foreman/models/state.py:45-79`, `src/foreman/models/events.py:36-72` |
| Chấm check, policy và giới hạn | `src/foreman/foreman/jev.py:15-35`, `src/foreman/policy.py:39-101` |
| Human escalation và steering | `src/foreman/responsibilities/builtin.py:73-138`, `src/foreman/runtime.py:432-506` |
| Observation và privacy | `src/foreman/observation.py:64-101`, `src/foreman/observation.py:176-295`, `src/foreman/observation.py:336-413` |
| Persistence và kiểm tra lại | `src/foreman/persistence.py:67-151`, `src/foreman/runtime.py:410-428` |
| Test nguồn và giới hạn chứng minh | `tests/test_policy.py:57-68`, `tests/test_runtime.py:43-71`, `docs/what-foreman-proves.md:36-47` |

## Hạn chế của phân tích

- Chỉ đọc source, test, docs, manifest và Git metadata tại HEAD nêu trên. Không chạy code, test, demo, script, cài dependency, dùng API Jev hay truy cập secret.
- Chưa xác minh hiệu năng, calibration, chất lượng worker/verifier, bảo mật toàn hệ thống hoặc tính tương thích runtime thực tế. Snapshot shallow không cho thấy lịch sử đầy đủ.
