---
repo: rocketride-org/rocketride-server
provider: github
canonical_id: github.com/rocketride-org/rocketride-server
url: https://github.com/rocketride-org/rocketride-server
aliases:
  - https://github.com/rocketride-org/rocketride-server.git
  - git@github.com:rocketride-org/rocketride-server.git
upstream: null
analyzed_at: 2026-09-28
analyzed_commit: 5a21c9c784ebee8f09cff59cb4acfcf5dbe77465
analysis_version: 1
status: analyzed
adoption: experiment
confidence: high
tags:
  - ai-agents
  - workflow-automation
  - agent-memory
  - evals
---

# Phân tích `rocketride-org/rocketride-server`

## Kết luận ngắn

RocketRide là một nền tảng dựng và chạy pipeline AI dạng đồ thị, gồm engine C++, node Python, SDK Python/TypeScript, MCP và giao diện IDE. Giá trị học hỏi lớn nhất cho workflow phần mềm có AI là **hợp đồng pipeline có kiểm tra, ranh giới gọi tool rõ ràng, vòng agent có giới hạn và log sự kiện có thể đọc lại**. Nên **`experiment`** với các pattern này trên một workflow nhỏ; chưa có căn cứ từ lượt đọc tĩnh để thay runtime hiện tại. [`docs/development/engine/index.md:1-3`, `packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:70-115`, `nodes/src/nodes/agent_rocketride/rocketride_agent.py:123-141`, `packages/ai/src/ai/modules/task/run_log.py:379-389`]

## Phạm vi và danh tính phiên bản

- Origin Git: `https://github.com/rocketride-org/rocketride-server.git`; nhánh checkout: `develop`; HEAD: `5a21c9c784ebee8f09cff59cb4acfcf5dbe77465`; commit có ngày `2026-09-25T12:52:04-07:00`. Xác minh bằng `git remote -v`, `git branch --show-current`, `git rev-parse HEAD`, `git show -s --date=iso-strict`. Đây là shallow clone (`git rev-parse --is-shallow-repository` trả `true`) và working tree nguồn sạch (`git status --porcelain=v1` không có dòng nào).
- Chỉ dùng source, test, tài liệu, manifest và Git metadata tại HEAD này. Không cài dependency, chạy code, script, test, benchmark hay truy cập secret.

## Repo làm gì

Dự án trình bày `.pipe` là JSON có source, các component và lane nối giữa chúng; người dùng có thể gọi pipeline qua SDK hoặc thao tác trong VS Code. Source tree đặt engine tại `packages/server`, tác vụ điều khiển và account tại `packages/ai`, node tại `nodes/src/nodes`, client tại `packages/client-*`. Đây là mô tả phạm vi từ repo, không xác nhận trải nghiệm triển khai thực tế. [`README.md:102-108`, `README.md:164-191`, `docs/development/engine/index.md:229-274`, `docs/README.md:8-22`]

## Kiến trúc và luồng chính

1. **Định nghĩa và kiểm tra đồ thị:** `PipelineConfig::validate` kiểm tra root, phiên bản, component, ID duy nhất, source và liên kết đầu vào/control trước khi chạy. Boundary này có ích để bắt lỗi cấu hình trước các bước AI tốn tiền hoặc có side effect. [`packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:70-115`, `packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:122-150`]
2. **Chạy và điều phối:** API task xác định team từ phiên đăng nhập, kiểm tra `task.control` trước khi gộp môi trường chứa secret. Ở tầng agent, host yêu cầu đúng một node LLM, lấy danh mục tool từ các node được nối, đặt tên tool theo node ID và gọi qua engine invoke. [`packages/ai/src/ai/modules/task/commands/cmd_task.py:127-164`, `packages/ai/src/ai/common/agent/_internal/host.py:37-59`, `packages/ai/src/ai/common/agent/_internal/host.py:70-124`]
3. **Agent theo wave:** planner trả danh sách tool call hoặc `done`; các call cùng wave được thực hiện đồng thời. Kết quả đầy đủ nằm trong memory, còn prompt wave sau nhận bản tóm tắt cấu trúc. Giới hạn mặc định là 10 wave rồi chuyển sang câu trả lời tổng hợp. Agent node còn có thể được gọi như tool của agent cha với schema đầu vào. [`nodes/src/nodes/agent_rocketride/rocketride_agent.py:7-27`, `nodes/src/nodes/agent_rocketride/rocketride_agent.py:46-74`, `nodes/src/nodes/agent_rocketride/rocketride_agent.py:123-234`, `nodes/src/nodes/agent_rocketride/IInstance.py:31-72`]
4. **Quan sát và đọc lại:** writer ghi event vào JSONL spool, seal thành segment và upload vào store; control file giữ vị trí segment và chapter theo run. MCP có các tool đọc chapter, event phân trang và trace từng object; mức trace `none` vẫn giữ chapter/console nhưng không có flow event. [`packages/ai/src/ai/modules/task/run_log.py:24-42`, `packages/ai/src/ai/modules/task/run_log.py:379-389`, `packages/ai/src/ai/modules/mcp/tools/logs.py:1-9`, `packages/ai/src/ai/modules/mcp/tools/logs.py:225-285`]

## Observed in code

- **Ranh giới agent/tool:** mọi lời gọi tool qua engine của driver đi qua `AgentBase.call_tool`; tùy chọn `require_tool_call` từ chối câu trả lời chỉ kể rằng đã dùng tool nhưng thực tế không gọi. Nó tắt theo mặc định, và bộ đếm tính cả lần gọi engine tool bị lỗi vì ghi nhận trước `invoke`. `memory.peek` là ngoại lệ local do executor xử lý trực tiếp, không đi qua adapter và không thỏa guard; test xác nhận hành vi này. [`packages/ai/src/ai/common/agent/agent.py:98-104`, `packages/ai/src/ai/common/agent/agent.py:206-215`, `packages/ai/src/ai/common/agent/agent.py:462-470`, `nodes/src/nodes/agent_rocketride/executor.py:528-594`, `packages/ai/tests/ai/common/agent/test_require_tool_call_integration.py:171-190`]
- **Khả năng hồi phục agent có giới hạn:** tool không tìm thấy được tra lại đúng node sở hữu một lần trước khi báo lỗi; exception từ tool được trả thành kết quả để planner thấy ở wave sau. Kết quả giống nhau chỉ được đánh dấu, không chặn gọi lặp; `max_waves` chỉ giới hạn số vòng đã hoàn tất. Executor khai báo timeout 120 giây nhưng đoạn chạy parallel dùng `as_completed()` và `future.result()` không truyền timeout/cancellation, nên một tool không trả về có thể giữ cả wave vô thời hạn và không bao giờ chạm `max_waves` hoặc synthesis fallback. [`packages/ai/src/ai/common/agent/_internal/host.py:136-158`, `nodes/src/nodes/agent_rocketride/executor.py:45-51`, `nodes/src/nodes/agent_rocketride/executor.py:591-630`, `nodes/src/nodes/agent_rocketride/rocketride_agent.py:123-141`]
- **Memory là một lựa chọn vận hành:** node `memory_persistent` mặc định dùng backend `memory`, có lựa chọn Redis và TTL cấu hình. Với `session_id`, nó đưa toàn bộ key trong session vào `question.metadata.memory_context`, rồi lưu nguyên văn câu trả lời thành `last_answer`; vì vậy cần xét phạm vi session, thời hạn lưu và nội dung nhạy cảm trước khi dùng. [`nodes/src/nodes/memory_persistent/IGlobal.py:37-52`, `nodes/src/nodes/memory_persistent/memory_store.py:616-658`, `nodes/src/nodes/memory_persistent/IInstance.py:59-99`, `nodes/src/nodes/memory_persistent/IInstance.py:118-145`]
- **Log bền vững nhưng có cửa sổ mất dữ liệu:** segment đã upload được tin cậy khi mở lại; segment còn ở spool nhưng mất theo container bị loại khỏi control. Code ghi rõ đây là cửa sổ mất dữ liệu chấp nhận được. Retention theo tuổi và số segment; cấu hình là 7 ngày cho dev, 30 ngày cho deploy, tối đa 64 segment 16 MB mỗi stream. Test mô phỏng crash xác nhận segment chỉ ở spool bị bỏ. [`packages/ai/src/ai/modules/task/run_log.py:629-692`, `packages/ai/src/ai/modules/task/run_log.py:1056-1084`, `packages/ai/src/ai/constants.py:66-90`, `packages/ai/tests/ai/modules/task/test_run_log.py:707-754`]
- **Security và privacy được xử lý theo boundary:** task kiểm tra quyền trên team trước khi giải secret; log read cần `task.monitor`, xóa cần `task.control`; MCP chỉ cho bypass auth dev khi bind loopback, từ chối credential trong query string. Bridge OpenTelemetry mặc định không xuất payload hoặc error text tự do, chỉ xuất nếu bật `include_content`. Các cơ chế này không thay thế đánh giá cấu hình deployment cụ thể. [`packages/ai/src/ai/modules/task/commands/cmd_task.py:127-164`, `packages/ai/src/ai/modules/task/commands/cmd_log.py:150-176`, `packages/ai/src/ai/modules/task/commands/cmd_log.py:325-339`, `packages/ai/src/ai/modules/mcp/auth.py:140-158`, `packages/ai/src/ai/modules/mcp/auth.py:253-263`, `packages/client-python/src/rocketride/otelbridge/mapper.py:280-298`, `packages/client-python/src/rocketride/otelbridge/mapper.py:713-730`]
- **Kiểm thử có nhiều tầng nhưng chưa được xác nhận chạy thành công ở HEAD này:** repo có unit/integration test cho guard agent và log recovery; workflow khai báo build ba OS, Ruff, gitleaks và các gate khác. Đây là cấu hình và mã test, không phải kết quả CI hay chất lượng đầu ra của model. [`packages/ai/tests/ai/common/agent/test_require_tool_call_integration.py:132-168`, `packages/ai/tests/ai/modules/task/test_run_log.py:707-754`, `.github/workflows/_build.yaml:55-85`, `docs/development/ci-gates.md:7-27`]

## Claimed by project

- README tuyên bố hơn 100 node, hơn 15 nhà cung cấp LLM, 9 vector DB, engine C++ đa luồng, pipeline chạy trên hạ tầng của người dùng và khả năng dùng ngay cho production. Chưa kiểm đếm toàn bộ node, đo throughput hay kiểm chứng vận hành production. [`README.md:18-23`, `README.md:70-79`]
- README giới thiệu pipeline mẫu xử lý tài liệu với model local nên dữ liệu không rời máy, đồng thời nói SDK dùng thông tin `.env` do extension ghi và sẽ fallback sang Cloud nếu chạy ngoài thư mục đó. Đó là lời mô tả của dự án; ở Python SDK, khi không có URI truyền vào và `ROCKETRIDE_URI` không tồn tại, code chọn endpoint Cloud mặc định. [`README.md:110-116`, `packages/client-python/src/rocketride/client.py:201-216`, `packages/client-python/src/rocketride/core/constants.py:61-66`]
- Tài liệu dự án mô tả quan sát call tree, token, memory và latency; cũng tuyên bố quy trình security scanning và SLA. Lượt đọc này chỉ xác nhận một số đường triển khai/log và file cấu hình, không xác minh dashboard, kết quả scan hay SLA thực tế. [`README.md:193-195`, `SECURITY.md:29-39`, `SECURITY.md:47-61`]

## Inferences

- **Độ chắc chắn cao:** pattern đáng chuyển sang workflow AI nội bộ là cấu hình đồ thị có validator + ranh giới gọi tool duy nhất + log theo event. Ba điểm này giúp tạo hợp đồng có thể kiểm tra và replay từng bước; hiệu quả thực tế trong `repo-learning` chưa được đo. [`packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:70-115`, `packages/ai/src/ai/common/agent/agent.py:462-470`, `packages/ai/src/ai/modules/task/run_log.py:379-389`]
- **Độ chắc chắn trung bình:** guard `require_tool_call` phát hiện một kiểu trả lời thiếu căn cứ, nhưng một tool call có lỗi vẫn tính là đã gọi và một tool trả dữ liệu sai vẫn qua guard. Vì vậy cần eval dựa trên kết quả/chứng cứ, không coi bộ đếm tool là kiểm chứng đáp án. [`packages/ai/src/ai/common/agent/agent.py:206-215`, `packages/ai/src/ai/common/agent/agent.py:462-470`, `nodes/src/nodes/agent_rocketride/executor.py:591-606`]
- **Độ chắc chắn trung bình:** thiết kế log phù hợp replay và phân tích lỗi, nhưng không nên coi là journal không mất dữ liệu cho action cần audit đầy đủ; spool chưa upload có thể mất khi host/container biến mất. [`packages/ai/src/ai/modules/task/run_log.py:629-692`, `packages/ai/tests/ai/modules/task/test_run_log.py:707-754`]

## Điểm mạnh

- Schema pipeline và nguồn/lane được kiểm tra trước khi engine dùng chúng. [`packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:70-115`, `packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:122-150`]
- Agent giữ kết quả lớn trong memory, đưa bản tóm tắt ngắn vào prompt và có giới hạn wave; lỗi tool được trả về cho planner. [`nodes/src/nodes/agent_rocketride/rocketride_agent.py:104-123`, `nodes/src/nodes/agent_rocketride/rocketride_agent.py:199-234`, `nodes/src/nodes/agent_rocketride/executor.py:591-606`]
- Log có chapter, vị trí sequence, retention và truy vấn qua MCP; có test cho retention và recovery. [`packages/ai/src/ai/modules/task/run_log.py:24-42`, `packages/ai/src/ai/modules/task/run_log.py:1056-1084`, `packages/ai/tests/ai/modules/task/test_run_log.py:628-679`, `packages/ai/tests/ai/modules/task/test_run_log.py:707-754`]

## Điểm yếu và rủi ro

- **Ranh giới local/cloud dễ bị hiểu sai:** Python SDK mặc định dùng endpoint Cloud nếu URI không được cấp; workflow yêu cầu dữ liệu ở local phải cấu hình URI rõ ràng và kiểm tra kết nối đích. [`packages/client-python/src/rocketride/client.py:201-216`, `packages/client-python/src/rocketride/core/constants.py:61-66`]
- **Memory và trace có thể chứa dữ liệu nhạy cảm:** memory node đưa mọi key của session vào metadata và lưu câu trả lời; log có thể lưu event payload tới mức trần 64 KB/event. Bridge OTel không xuất nội dung theo mặc định, nhưng `include_content=True` mở việc này. Cần phân loại dữ liệu, TTL, phân quyền đọc và mức trace trước khi thử với dữ liệu thật. [`nodes/src/nodes/memory_persistent/IInstance.py:79-93`, `nodes/src/nodes/memory_persistent/IInstance.py:138-145`, `packages/ai/src/ai/constants.py:83-85`, `packages/client-python/src/rocketride/otelbridge/mapper.py:280-298`]
- **Chi phí áp dụng:** kiến trúc đa ngôn ngữ với engine C++, Python node, SDK và nhiều app cùng pipeline yêu cầu vận hành, build và debug qua nhiều boundary; CI khai báo ba OS và timeout 90 phút. Phù hợp để học pattern trước khi cân nhắc tích hợp nền tảng. [`docs/development/engine/index.md:229-274`, `.github/workflows/_build.yaml:55-85`]

## Recommendations

| Ý tưởng cho workflow AI | Thử nghiệm và trade-off |
|---|---|
| **Validator trước thực thi** | Tạo schema cho bước, input/output, quyền và liên kết dependency; chặn cấu hình lỗi trước model/tool call. Cần duy trì schema đồng bộ với executor. [`packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:70-115`] |
| **Tool seam duy nhất** | Bắt tất cả tool call đi qua một adapter ghi tên tool, input đã lọc, thời gian, trạng thái và kết quả; thêm guard yêu cầu chứng cứ cho task cần tool. Bộ đếm lời gọi chỉ là tín hiệu sơ cấp. [`packages/ai/src/ai/common/agent/agent.py:206-215`, `packages/ai/src/ai/common/agent/agent.py:462-470`] |
| **Wave có ngân sách và state gọn** | Thử giới hạn vòng, deadline/cancellation thực cho từng tool và cả wave, trả lỗi tool về planner, giữ dữ liệu lớn ngoài prompt; đo chi phí token, tỷ lệ hoàn thành, timeout, lỗi lặp và chất lượng đáp án. Cần tránh để fallback tổng hợp biến thất bại thành câu trả lời có vẻ chắc chắn. [`nodes/src/nodes/agent_rocketride/rocketride_agent.py:104-123`, `nodes/src/nodes/agent_rocketride/rocketride_agent.py:199-234`, `nodes/src/nodes/agent_rocketride/executor.py:45-51`, `nodes/src/nodes/agent_rocketride/executor.py:591-630`] |
| **Event replay có retention rõ** | Lưu event theo run/sequence, cho phép đọc lại và tạo eval từ failure; đặt retention và chính sách payload. Nếu action cần audit không mất dữ liệu, bổ sung cơ chế xác nhận ghi bền vững trước side effect. [`packages/ai/src/ai/modules/task/run_log.py:24-42`, `packages/ai/src/ai/modules/task/run_log.py:629-692`, `packages/ai/src/ai/constants.py:66-90`] |

Thử một pipeline giả lập gồm agent → tool đọc tài liệu → validator → trả lời; dùng câu hỏi có đáp án biết trước, tool ném lỗi, tool không trả về và dữ liệu nhạy cảm giả lập. Chỉ mở rộng sau khi đo được tỷ lệ đúng, số lần gọi tool thừa, hành vi timeout/cancellation và nội dung xuất hiện trong log. Đây là đề xuất thử nghiệm cho workflow, không phải kết quả đã có của dự án. [`packages/ai/tests/ai/common/agent/test_require_tool_call_integration.py:132-190`, `packages/ai/tests/ai/modules/task/test_run_log.py:707-754`]

## Quyết định áp dụng

**`experiment`** với pattern validator, tool seam, vòng agent giới hạn và event replay; chưa áp dụng toàn bộ runtime. Lý do: code và test cho thấy cơ chế đáng học, nhưng lượt phân tích không chạy hệ thống; endpoint Cloud mặc định và cửa sổ mất log chưa upload cần được kiểm soát theo yêu cầu dữ liệu/audit của workflow đích. [`packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:70-115`, `packages/ai/tests/ai/common/agent/test_require_tool_call_integration.py:132-168`, `packages/client-python/src/rocketride/client.py:201-216`, `packages/ai/src/ai/modules/task/run_log.py:629-692`]

## Evidence map

| Nhận định | Nguồn |
|---|---|
| Validator pipeline | `packages/server/engine-lib/engLib/store/pipeline/pipeline_config.cpp:70-150` |
| API task và quyền | `packages/ai/src/ai/modules/task/commands/cmd_task.py:127-164`, `packages/ai/src/ai/modules/task/commands/cmd_log.py:150-176` |
| Tool seam và guard | `packages/ai/src/ai/common/agent/_internal/host.py:70-124`, `packages/ai/src/ai/common/agent/agent.py:206-215`, `packages/ai/src/ai/common/agent/agent.py:462-470` |
| Wave loop, nested agent | `nodes/src/nodes/agent_rocketride/rocketride_agent.py:123-234`, `nodes/src/nodes/agent_rocketride/IInstance.py:31-72` |
| Memory | `nodes/src/nodes/memory_persistent/IGlobal.py:37-52`, `nodes/src/nodes/memory_persistent/IInstance.py:59-145` |
| Log/recovery/retention | `packages/ai/src/ai/modules/task/run_log.py:629-692`, `packages/ai/src/ai/modules/task/run_log.py:1056-1120`, `packages/ai/src/ai/constants.py:66-90` |
| Endpoint mặc định | `packages/client-python/src/rocketride/client.py:201-216`, `packages/client-python/src/rocketride/core/constants.py:61-66` |
| Privacy bridge | `packages/client-python/src/rocketride/otelbridge/mapper.py:280-298`, `packages/client-python/src/rocketride/otelbridge/mapper.py:713-730` |
| Test và CI | `packages/ai/tests/ai/common/agent/test_require_tool_call_integration.py:132-168`, `packages/ai/tests/ai/modules/task/test_run_log.py:707-754`, `.github/workflows/_build.yaml:55-85` |

## Hạn chế của phân tích

- Chỉ đọc các file tiêu biểu trong repo lớn tại một shallow HEAD; không rà soát toàn bộ node, deployment config hay từng đường auth. Không chạy repo, test, benchmark hoặc kiểm chứng kết quả CI.
- Các tuyên bố về số node, hiệu năng, production readiness, trải nghiệm Cloud và SLA chỉ là claim của dự án. [`README.md:18-23`, `README.md:70-79`, `SECURITY.md:29-39`]
- Kết luận về cửa sổ mất log dựa trên source và test mô phỏng, chưa đo trên một deployment thật. [`packages/ai/src/ai/modules/task/run_log.py:629-692`, `packages/ai/tests/ai/modules/task/test_run_log.py:707-754`]
