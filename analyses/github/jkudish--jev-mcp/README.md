---
repo: jkudish/jev-mcp
provider: github
canonical_id: github.com/jkudish/jev-mcp
url: https://github.com/jkudish/jev-mcp
aliases:
  - https://github.com/jkudish/jev-mcp.git
  - git@github.com:jkudish/jev-mcp.git
upstream: null
analyzed_at: 2026-09-28
analyzed_commit: 417acfa1ea84d0cccae935007bfd16970d676816
analysis_version: 1
status: analyzed
adoption: experiment
confidence: high
tags:
  - ai-agents
  - evidence-grounding
  - retrieval
  - workflow-automation
---

# Phân tích `jkudish/jev-mcp`

## Kết luận ngắn

`jev-mcp` là MCP server đưa 11 phép phán đoán có cấu trúc của model Jev vào workflow agent: kiểm tra claim với evidence, sàng lọc nội dung ngoài, tìm và phân loại theo nghĩa, trích xuất giá trị, đánh giá patch và kiểm tra claim hoàn tất. Nó trả xác suất/điểm và action; agent hoặc hệ thống gọi công cụ vẫn chịu trách nhiệm thực thi policy. Đây là phạm vi công cụ được công bố trong README và được hiện thực bằng 11 lần đăng ký tool trong `src/index.ts`. [`README.md:10-26`; `src/index.ts:161-162`; `src/index.ts:1534-1536`]

Năm bài học áp dụng cho workflow AI:

1. **Kiểm tra claim theo từng mệnh đề.** Tách `supports`, `contradicts`, `says_nothing`; evidence im lặng không được biến thành “đúng”. [`src/index.ts:202-220`; `src/lib.ts:63-68`]
2. **Tách model khỏi policy.** Model trả phân phối; code kiểm tra response và quyết định `auto`, `review`, `escalate` bằng ngưỡng rõ ràng. [`src/index.ts:1327-1357`; `src/lib.ts:296-393`]
3. **Cho phép “không có đáp án”.** Tìm kiếm ngữ nghĩa hỏi cả “ứng viên tốt nhất” lẫn “có ứng viên nào trả lời không”; quyết định giới hạn có `ask_user`/`investigate`/`none`. [`src/index.ts:501-540`; `src/index.ts:776-847`]
4. **Dùng kiểm tra cơ học trước phán đoán ngữ nghĩa.** Trích xuất bắt đầu bằng regex trong worker có timeout; model chỉ chọn giữa các substring thật sự tìm thấy. [`src/lib.ts:410-480`; `src/index.ts:1110-1161`]
5. **Trước khi tuyên bố xong, kiểm patch và claim bằng evidence thật.** `jev_gate` kết hợp review diff với verification từng claim; input bị cắt, response lỗi hay claim bị phản bác không thể tự động thông qua. [`src/index.ts:1534-1545`; `src/index.ts:1607-1675`]

**Quyết định:** `experiment`. Nên học ngay các contract và ranh giới trên, rồi thử công cụ thật trên bộ case nhỏ có đáp án do người kiểm tra. Chưa nên đưa xác suất Jev thành cổng chặn tự động cho việc quan trọng: project nói chính các ngưỡng là điểm khởi đầu cần hiệu chỉnh, còn `confidence` của Choice/Score đo độ tập trung phân phối, không phải xác suất câu trả lời đúng. [`README.md:650-659`]

## Repo làm gì

Dự án đóng gói model Jev thành MCP server Node.js/TypeScript, yêu cầu Node `>=22`; package tại checkout là `@jkudish/jev-mcp` phiên bản `0.10.1`, MIT. Tool được nhóm theo việc agent thường làm: `verify`, `screen`, `noul`, `find`, `rerank`, `classify`, `decide`, `compare`, `extract`, `review`, `gate`. [`package.json:2-4`; `package.json:23-31`; `LICENSE:1-8`; `README.md:12-24`]

Người dùng mục tiêu là coding/knowledge agent đã có nội dung, diff hoặc tập ứng viên và cần phán đoán rẻ, có dạng dữ liệu ổn định để điều phối. Server nhận input qua MCP stdio mặc định hoặc HTTP tùy chọn; các phán đoán được gửi tới provider Jev cấu hình qua environment. [`README.md:28-39`; `src/index.ts:1711-1718`; `src/provider.ts:218-250`]

## Kiến trúc và luồng chính

```text
Agent + skill hướng dẫn lúc gọi
  → MCP tool schema chặt
  → state + Choice/Noul/Score questions
  → provider adapter → Jev
  → kiểm envelope, answer, phân phối
  → policy code: auto / review / escalate
  → agent thực thi hoặc hỏi người dùng
```

`src/index.ts` định nghĩa tool, dựng câu hỏi, chuẩn hóa response và xuất JSON qua MCP. Đăng ký tool được lưu một lần rồi phát lại vào `McpServer` mới cho từng kết nối stdio hoặc HTTP request stateless. `src/provider.ts` chọn provider và gửi `{state, questions}`; `src/lib.ts` chứa helper và policy có thể unit-test độc lập. [`src/index.ts:84-119`; `src/provider.ts:1-16`; `src/lib.ts:1-9`]

Skill đi kèm xử lý phần “khi nào gọi”: nó phân biệt exact search với semantic selection, `find` với `rerank`, `verify` với `gate`, và nhắc agent rằng kết quả chỉ tư vấn, policy nằm ở bên gọi. Đây là cơ chế tăng khả năng tool được dùng đúng chỗ, không phải một tool mới của server. [`skills/jev/SKILL.md:11-31`; `skills/jev/SKILL.md:33-46`]

## Observed in code

- **Input và output có contract chặt.** Top-level input dùng Zod `.strict()` nên typo thành lỗi. Choice answer phải có đúng tập key, xác suất hữu hạn trong `[0,1]` cộng gần 1 và `choice` là argmax; Noul phải là xác suất hữu hạn. Envelope rỗng được chuẩn hóa để từng tool đi vào nhánh `invalid_response`. [`src/index.ts:108-125`; `src/index.ts:1327-1357`]
- **Verification không gộp “thiếu bằng chứng” với lỗi giao thức.** `jev_verify` đặt ba relation `supports`/`contradicts`/`says_nothing`; response thiếu hoặc sai cho ra `verdict: unknown`, `status: invalid_response`, `action: review`, còn `says_nothing` thành `unsupported`. Khi có nhiều evidence, source id được hỏi riêng. [`src/index.ts:193-220`; `src/index.ts:230-265`; `src/lib.ts:63-72`]
- **Screen là recommendation, không phải bộ chặn tự vận hành.** Code phán đoán injection, substance và relevance tùy purpose; thiếu answer thành `review`. Policy ưu tiên `block`/`review` khi injection cao, sau đó mới `skip` nội dung rỗng hoặc lạc đề. Tool chỉ trả action qua JSON. [`src/index.ts:289-363`; `src/lib.ts:81-98`]
- **Semantic find có existence check.** `best` luôn là Choice trên ứng viên, còn Noul `exists` cho biết liệu tập có câu trả lời. Response thiếu một trong hai là lỗi; rank chỉ được công bố khi cả hai hợp lệ. [`src/index.ts:478-540`]
- **Classification theo lô nhưng vẫn giữ identity.** Catalog nằm một lần trong shared state; mỗi item thành một Choice. Code giữ external ID, dùng wire key nội bộ, giới hạn `items × classes <= 8000`; `auto` đòi top probability và margin đủ ngưỡng, item lỗi được đánh `invalid_response` riêng. [`src/index.ts:550-581`; `src/index.ts:588-655`; `src/index.ts:658-714`]
- **Decision có lối thoát.** `jev_decide` bắt buộc evidence, priorities và 2–6 phương án; mặc định thêm `ask_user`/`investigate`/`none`, kiểm từng requirement riêng và cảnh báo khi requirement mâu thuẫn với lựa chọn được đề xuất. [`src/index.ts:723-753`; `src/index.ts:776-853`]
- **Extraction tránh model tự viết giá trị.** Regex chạy trong worker có timeout 1 giây, deduplicate và giới hạn candidate; model chỉ chọn candidate hoặc `none_of_them`. Khi tập candidate bị cắt hoặc có match quá dài, kết quả không thể `auto`. [`src/lib.ts:410-480`; `src/index.ts:1142-1219`]
- **Completion gate ghép hai loại evidence.** `jev_review` tính điểm correctness/spec match/test gap/blast radius và `safe_to_apply`; `jev_gate` thêm kiểm claim chỉ từ trường `evidence`. Code chặn `auto` khi context bị cắt, response sai, confidence thấp hoặc có claim bị phản bác. Nó không chạy test hay áp patch. [`src/index.ts:1469-1531`; `src/index.ts:1534-1545`; `src/index.ts:1623-1704`; `src/lib.ts:321-393`]
- **HTTP transport có ranh giới vận hành.** Mặc định bind loopback; bind ra ngoài phải có bearer token. Nó kiểm Host/Origin trên loopback, so token bằng `timingSafeEqual`, giới hạn in-flight và trả `429` khi quá tải. [`src/http.ts:39-57`; `src/http.ts:59-114`]
- **Test suite được định nghĩa nhưng chưa chạy trong lượt này.** Package có unit, mock, provider, regression và HTTP tests; CI cấu hình typecheck, build, test và E2E tùy API key. Mock test dùng local HTTP server và MCP client để tạo response kiểm soát. [`package.json:26-31`; `.github/workflows/ci.yml:8-24`; `test/mock.test.mjs:1-12`; `test/mock.test.mjs:21-78`]

## Claimed by project

- README tự mô tả mỗi judgment có độ trễ khoảng 150–500 ms và giá dưới một cent; lượt này không benchmark hay gọi provider để xác minh. [`README.md:10-26`]
- Dự án gọi output là “calibrated probability distributions”, đồng thời giải thích `confidence` của Choice/Score là độ nhọn của phân phối, không phải xác suất đúng, và ngưỡng phải chỉnh theo dữ liệu riêng. Không có đánh giá calibration độc lập trong lượt này. [`README.md:650-659`]
- README nêu server HTTP tương thích MCP 2026-07-28 và client 2025, có thể scale stateless; source và test cho thấy thiết kế tương ứng nhưng lượt này không chạy interoperability test. [`README.md:131-145`; `src/http.ts:1-10`; `test/http.test.mjs:52-73`]
- Skill khuyên gọi tool cho các phán đoán verification/guardrail ngay cả khi agent thấy “hiển nhiên”; đây là hướng dẫn của dự án, chưa chứng minh giảm lỗi trong workflow của thư viện này. [`skills/jev/SKILL.md:13-15`]

## Inferences

- **Độ tin cậy: cao về interface, thấp hơn về chất lượng phán đoán.** Source xác nhận shape validation và policy; mức đúng thực tế của model cần case có ground truth, đặc biệt cho claim ngầm hiểu, prompt injection và patch review. [`src/index.ts:1327-1357`; `README.md:654-659`]
- **MCP tool chỉ hữu ích nếu agent có trigger rõ.** Repo đặt rule chọn tool trong skill riêng, cho thấy tác giả xử lý khoảng cách giữa “tool đã đăng ký” và “agent gọi đúng lúc”; tác động thực tế lên agent khác là suy luận, chưa được đo ở đây. [`skills/jev/SKILL.md:13-31`; `README.md:147-157`]
- **Boundary “evidence only” của `jev_gate` là ràng buộc bằng prompt trong cùng một model call.** Code đặt request, diff, tests, claims và evidence cùng `state`, rồi yêu cầu câu hỏi claim chỉ dùng evidence; đây không phải cách ly dữ liệu cứng. Tài liệu skill cũng ghi nhận giới hạn này. [`src/index.ts:1614-1636`; `skills/jev/reference/tools.md:95-101`]

## Điểm mạnh

1. Phân biệt protocol failure với kết quả ngữ nghĩa (`unsupported`, `absent`, `not_found`), tránh cho lỗi model/provider bị đọc nhầm thành quyết định hợp lệ. [`src/index.ts:242-265`; `src/index.ts:513-529`; `src/index.ts:1192-1214`]
2. Policy có ngưỡng và đường `review`/`escalate` rõ; input bị truncate không được tự động thông qua. [`src/lib.ts:296-393`; `src/index.ts:1607-1612`]
3. Các tác vụ có cấu trúc tái dùng được ở nhiều workflow: claim verification, retrieval, task routing và completion gate; skill diễn đạt lúc chọn công cụ và lúc dùng kiểm tra cơ học. [`skills/jev/SKILL.md:17-45`]
4. Provider fetch-based có deadline chung, retry hữu hạn theo HTTP status cho phép; lỗi mạng mơ hồ không tự gửi lại paid request. Đây là lựa chọn thận trọng về chi phí và idempotency. [`src/provider.ts:39-49`; `src/provider.ts:188-216`]

## Điểm yếu và rủi ro

- **Privacy và chi phí provider.** Input (`state`, `questions`) được gửi tới provider đã cấu hình; skill nói rõ không gửi secret hoặc source riêng tư nếu policy không cho phép. Vì vậy dữ liệu repo nội bộ, log và diff cần redaction/approval trước khi thử. [`src/provider.ts:239-250`; `src/provider.ts:338-348`; `skills/jev/SKILL.md:53-57`; `SECURITY.md:13-17`]
- **Phán đoán không là bằng chứng thực nghiệm.** Score review dựa trên request/diff/test output được *báo cáo*, không tự chạy test; model có thể cho xác suất cao mà vẫn sai. `confidence` không phải xác suất đúng. [`src/index.ts:1473-1479`; `src/index.ts:1515-1528`; `README.md:654-659`]
- **Screen không tự chặn dữ liệu.** Consumer phải thực thi `block`/`review` và vẫn coi nội dung `pass` là data chứ không phải instruction. Nếu agent bỏ qua action, lớp bảo vệ không phát huy tác dụng. [`src/index.ts:353-363`; `skills/jev/SKILL.md:33-36`]
- **Giới hạn ngữ cảnh có thể bỏ sót thông tin.** `find` chỉ nhận tối đa 250 candidate và cắt mỗi text tại 2.000 ký tự; review/gate cắt đầu vào dài. Code hạ `auto` khi review/gate bị cắt, nhưng caller vẫn phải chọn chunk có bằng chứng cần thiết. [`src/index.ts:147-156`; `src/index.ts:494-499`; `src/index.ts:1607-1621`; `src/lib.ts:321-324`]
- **Phụ thuộc release/provider.** Package cần Node 22 và nhiều dependency; ví dụ cài đặt bằng `npx -y @jkudish/jev-mcp` lấy phiên bản do registry phục vụ lúc chạy. Nếu thử trong workflow có yêu cầu tái lập, nên pin version và ghi provider/model. [`package.json:23-54`; `README.md:49-64`; `src/index.ts:79-82`]
- **Thiếu kiểm chứng runtime trong lượt này.** Có test và CI config, nhưng không có kết quả test/benchmark được chạy tại checkout này; CI definition không chứng minh trạng thái xanh ở HEAD. [`package.json:26-31`; `.github/workflows/ci.yml:8-24`]

## Recommendations

1. **Adopt pattern ngay trong quy trình phân tích repo (chi phí thấp):** với mỗi claim quan trọng, lưu claim, evidence `path:line-line`, trạng thái `supported`/`contradicted`/`unsupported`/`unresolved`. Dùng kiểm tra deterministic cho URL, quote, SHA và line range trước khi xin model đánh giá suy luận. Pattern dựa trên relation ba nhánh và việc tách lỗi giao thức khỏi kết luận. [`src/index.ts:202-265`; `skills/jev/SKILL.md:21-24`]
2. **Thử `verify` trên 20–30 claim đã được người gán nhãn (chi phí API nhỏ, có review):** chọn claim trực tiếp, claim suy diễn, evidence im lặng và evidence phản bác; so verdict với nhãn người và ghi false pass/false block. Chỉ hiệu chỉnh `auto_accept` sau khi có dữ liệu, đúng cảnh báo của dự án. [`README.md:650-659`; `src/index.ts:171-183`]
3. **Dùng existence gate cho retrieval (chi phí thấp đến vừa):** `rg`/exact search trước; nếu cần tìm theo nghĩa, xếp hạng candidate kèm câu hỏi “có câu trả lời không”. Không trình bày top hit khi `exists_verdict` là `absent` hoặc call lỗi. [`src/index.ts:501-540`; `skills/jev/SKILL.md:24-25`; `skills/jev/SKILL.md:38-41`]
4. **Gắn completion claim với log/source thật (chi phí vừa):** trước khi tuyên bố “test pass” hay “đã sửa”, chạy check thực tế, lưu output, đối chiếu diff và claim. Có thể thử `jev_gate` như reviewer bổ sung; không dùng `action: auto` thay cho test, code review hay quyền quyết định của user. [`src/index.ts:1534-1545`; `src/index.ts:1623-1675`; `skills/jev/SKILL.md:44-46`]
5. **Nếu dùng screen trên nội dung ngoài, enforce ở caller (chi phí vừa):** giữ nguồn ngoài là data, đọc `recommendation.action`, và định nghĩa rõ cách xử lý `invalid_response`/`review`/`block`. Không đẩy nguyên source nhạy cảm sang provider. [`src/index.ts:338-361`; `skills/jev/SKILL.md:35-36`; `skills/jev/SKILL.md:53-57`]

## Quyết định áp dụng

**`experiment` cho package; adopt-now cho các pattern không phụ thuộc model.** Tool có interface tốt và nhiều failure path được xử lý bằng code, đủ đáng thử trong môi trường nhỏ. Nhưng latency/giá/calibration chưa được kiểm chứng tại checkout này, và việc gửi input tới provider có ranh giới dữ liệu cần quản lý. Chỉ cân nhắc dùng làm gate tự động sau khi có eval riêng, ngưỡng đạt yêu cầu và policy dữ liệu rõ. [`src/index.ts:1327-1357`; `src/lib.ts:321-393`; `README.md:26-26`; `README.md:654-659`; `SECURITY.md:13-17`]

## Evidence map

| Nhận định | Nguồn |
|---|---|
| Danh sách 11 công cụ, phạm vi dự án | `README.md:10-26`, `src/index.ts:161-162`, `src/index.ts:1534-1536` |
| MCP server và provider boundary | `src/index.ts:84-119`, `src/provider.ts:218-250`, `src/index.ts:1711-1718` |
| Verification và failure branch | `src/index.ts:202-265`, `src/lib.ts:63-72` |
| Screen, find, classify, decide | `src/index.ts:289-363`, `src/index.ts:478-540`, `src/index.ts:550-714`, `src/index.ts:723-853` |
| Regex trước model | `src/lib.ts:410-480`, `src/index.ts:1110-1219` |
| Review và completion gate | `src/index.ts:1252-1357`, `src/index.ts:1469-1704`, `src/lib.ts:296-393` |
| Skill điều phối agent | `skills/jev/SKILL.md:13-57` |
| Data egress và HTTP boundary | `src/provider.ts:338-348`, `src/http.ts:39-114`, `SECURITY.md:13-17` |
| Test intent và CI | `test/mock.test.mjs:1-78`, `test/http.test.mjs:43-73`, `.github/workflows/ci.yml:8-24` |

## Hạn chế của phân tích

- Phân tích checkout shallow `main` tại `417acfa1ea84d0cccae935007bfd16970d676816` (commit time `2026-09-26T23:41:22Z`), origin `https://github.com/jkudish/jev-mcp.git`; working tree sạch lúc đọc. Git metadata đã được kiểm tra bằng `git remote -v`, `git rev-parse HEAD`, `git branch --show-current`, `git status --short`, `git show -s`.
- Chỉ đọc source/docs/tests/Git metadata. Không chạy code, test, script, installer hoặc dependency của repo; không gọi Jev API. Chưa xác minh hành vi live, latency, giá, calibration, tương thích MCP thực tế hay trạng thái CI ở commit này.
- Không audit toàn bộ 1.718 dòng `src/index.ts` và 2.284 dòng mock test theo từng nhánh; tập trung vào những luồng liên quan trực tiếp đến workflow agent. Provider TypeSafe/Vercel đi qua package ngoài `@jkudish/jev-agent-tools`, nên hành vi nội bộ dependency đó nằm ngoài phạm vi. [`package.json:44-54`; `src/provider.ts:247-290`]
