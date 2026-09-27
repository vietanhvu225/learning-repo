---
repo: anishfn/shapeshift
provider: github
canonical_id: github.com/anishfn/shapeshift
url: https://github.com/anishfn/shapeshift
aliases:
  - https://github.com/anishfn/shapeshift.git
  - git@github.com:anishfn/shapeshift.git
upstream: null
analyzed_at: 2026-09-28
analyzed_commit: 5e24166dcbde6e794f0bd5b1b4bd395aaee5fc19
analysis_version: 1
status: analyzed
adoption: experiment
confidence: medium
tags:
  - workflow-automation
  - local-first
---

# Phân tích `anishfn/shapeshift`

## Kết luận ngắn

Shapeshift là ứng dụng nhập liệu một ô: khi người dùng gõ, nó phân loại ý định rồi hiện thẻ phù hợp (lịch hẹn, nhắc việc, phép tính, chia tiền, ghi chú...). Đáng học cho workflow làm việc với AI là **giới hạn vai trò model vào phân loại có cấu trúc**, để code kiểm tra, tính toán và quyết định hành động; **giữ giao diện ổn định trước kết quả thay đổi liên tục**; và **có classifier offline cùng contract đầu ra**. Đây là mẫu thiết kế để thử nghiệm, chưa phải thư viện có thể đưa thẳng vào quy trình phân tích repo. `README.md:1-22`, `src/lib/jev/questions.ts:3-13`, `src/lib/parse/index.ts:46-80`, `src/lib/decide.ts:3-18`

Quyết định: **`experiment`** với một prototype nhỏ cho bước định tuyến yêu cầu AI (ví dụ “phân tích repo”, “so sánh”, “tạo báo cáo”, “cập nhật”), không sao chép ngưỡng confidence hay giả định classifier offline của dự án phù hợp với tiếng Việt. `src/lib/decide.ts:9-18`, `src/lib/jev/mock.ts:27-39`, `src/lib/jev/mock.ts:42-105`

## Phạm vi và danh tính phiên bản

- Origin đã xác minh: `https://github.com/anishfn/shapeshift.git`.
- Branch: `main`; HEAD: `5e24166dcbde6e794f0bd5b1b4bd395aaee5fc19`.
- Checkout shallow, working tree sạch tại thời điểm đọc. Metadata được kiểm tra bằng `git remote -v`, `git rev-parse HEAD`, `git branch --show-current`, `git status --short`.
- Đây là ứng dụng Next.js riêng (`private: true`, version `0.1.0`), không phải package API công khai. `package.json:1-5`, `package.json:15-35`

Mọi dẫn chiếu `path:line-line` dưới đây tương đối với root của checkout tại commit trên.

## Repo làm gì

Đầu vào ngôn ngữ tự nhiên được phân thành 19 loại thẻ cộng `none`; ví dụ event, reminder, todo, timer, convert, calc, poll, goal và note. Người dùng có thể chấp nhận gợi ý, chọn ý định bằng tay, lưu thẻ rồi mở lại để sửa. Dữ liệu đã lưu nằm trong `localStorage` của trình duyệt. `src/lib/jev/types.ts:3-26`, `src/components/shapeshift/Shapeshift.tsx:132-168`, `src/lib/savedItems.ts:4-14`, `src/lib/savedItems.ts:21-27`

Mục tiêu sản phẩm và các ví dụ do dự án mô tả ở `README.md:1-18`, `README.md:51-75`; báo cáo này chưa kiểm tra demo chạy thực tế.

## Kiến trúc và luồng chính

```text
Văn bản người dùng
  → debounce / hủy request cũ / cache phía client
  → POST /api/intent
  → Jev online hoặc classifier keyword offline
  → kết quả có schema: intent + confidence + signals
  → state machine: input | ghost | choose | committed
  → chỉ lấy signals cần cho thẻ đã chọn
  → parser cục bộ trích giá trị và tính kết quả
  → component trong registry hiển thị; người dùng lưu/chỉnh sửa
```

Hook `useIntent` debounce mặc định 120 ms, abort request trước, dùng request id để bỏ kết quả cũ và cache 300 mục. Server kiểm tra request tối đa 2.000 ký tự, dùng cache 500 mục cho kết quả online, gọi Jev một lần cho 14 câu hỏi hoặc dùng mock khi không có key. Khi API lỗi, client chuyển về classifier offline. `src/hooks/useIntent.ts:20-49`, `src/hooks/useIntent.ts:52-121`, `src/app/api/intent/route.ts:8-39`, `src/lib/jev/client.ts:47-75`, `src/lib/jev/questions.ts:98-102`

Sau phân loại, `decide` chọn giữa input, preview mờ, hai lựa chọn và thẻ đã chốt; `gateSignals` chỉ giữ tín hiệu mà loại thẻ dùng. `parseFor` và `registry` giữ parser, mức độ đủ dữ liệu, nhãn, summary và component theo ý định. `src/lib/decide.ts:3-18`, `src/lib/decide.ts:54-77`, `src/lib/signals.ts:79-102`, `src/lib/parse/index.ts:46-80`, `src/components/intents/registry.ts:261-261`

## Observed in code

1. Schema Jev đặt tiêu chí ý định tương đối tách biệt, có `none` cho đầu vào chưa rõ và các câu hỏi riêng cho readiness, urgency, tone, mode. Comment yêu cầu model không trích số, đếm hay tính ngày; đó là contract thiết kế, còn chất lượng model chưa được đo trong lượt đọc này. `src/lib/jev/questions.ts:3-10`, `src/lib/jev/questions.ts:13-49`
2. Kết quả model được chuẩn hóa thành `IntentResult`; response từ API được kiểm tra bằng Zod ở client. Nhánh offline tạo cùng hình dạng kết quả và test đối chiếu số câu hỏi với schema. `src/lib/jev/types.ts:52-97`, `src/hooks/useIntent.ts:46-49`, `src/lib/jev/mock.ts:152-158`, `src/lib/__tests__/mock.test.ts:43-50`
3. Jev được gọi phía server bằng `systemOne({ state: { text }, questions })`; key nằm trong biến môi trường phía server, client file import `server-only`. Client SDK đặt timeout 2,5 giây và không retry. `src/lib/jev/client.ts:1-3`, `src/lib/jev/client.ts:19-38`, `src/lib/jev/client.ts:47-50`
4. Giá trị có thể kiểm chứng được xử lý bằng parser: registry ánh xạ 19 intent đến parser; phép tính dùng tokenizer, shunting-yard và đánh giá RPN, không gọi `eval`. `src/lib/parse/index.ts:22-80`, `src/lib/parse/calc.ts:22-65`, `src/lib/parse/calc.ts:94-112`
5. Với kết quả mới chưa có override, `rawState` tự commit khi confidence đạt 0,7; sau đó challenger cần thắng hai lần để thay thẻ, trừ trường hợp đạt 0,85. Người dùng chọn tay hoặc nhấn Tab có thể commit không qua ngưỡng 0,7; lựa chọn ép được giữ qua sửa nhỏ. Tín hiệu phụ có ngưỡng bật/tắt riêng. Các test nguồn bao phủ challenger thoáng qua, hai lần thắng, override, lựa chọn ép và hysteresis của badge. `src/lib/decide.ts:9-18`, `src/lib/decide.ts:54-77`, `src/lib/decide.ts:84-134`, `src/lib/signals.ts:15-23`, `src/lib/signals.ts:61-102`, `src/lib/__tests__/decide.test.ts:34-64`, `src/lib/__tests__/signals.test.ts:20-41`
6. Thẻ lưu nguyên văn đầu vào, loại thẻ và summary trong `localStorage`; chế độ demo chỉ giữ trong bộ nhớ. `src/lib/savedItems.ts:4-18`, `src/lib/savedItems.ts:21-27`, `src/lib/savedItems.ts:52-68`

## Claimed by project

- README gọi cách tiếp cận là “Jev decides, code computes” và nói 14 câu hỏi được trả lời trong một call. Code cho thấy một `systemOne` với schema 14 câu hỏi, nhưng chưa đo latency hoặc chất lượng thực tế của dịch vụ. `README.md:18-22`, `src/lib/jev/client.ts:47-50`, `src/lib/jev/questions.ts:11-102`
- Dự án tuyên bố chạy offline mặc định, không cần tài khoản, và fallback khi API không truy cập được. Code xác nhận nhánh thiếu key và fallback ở client, nhưng chưa thử hoạt động end-to-end. `README.md:22-22`, `README.md:35-42`, `src/lib/jev/client.ts:19-23`, `src/hooks/useIntent.ts:32-49`
- README mô tả 19 loại thẻ và thao tác bàn phím; đây là tính năng được tài liệu công bố, chưa kiểm tra bằng UI. `README.md:51-87`

## Inferences

- **Mức tin cậy cao:** Ranh giới “AI chọn loại tác vụ, code làm việc xác định” có thể giảm lỗi số học và giúp agent không tự ý suy diễn dữ liệu. Suy luận này dựa trên schema cấm model trích giá trị và parser riêng, không phải benchmark chứng minh tỷ lệ lỗi giảm. `src/lib/jev/questions.ts:3-10`, `src/lib/parse/index.ts:51-80`
- **Mức tin cậy vừa:** Cùng pattern có thể làm bước định tuyến yêu cầu trong workflow AI: model trả về loại tác vụ và mức tin cậy, sau đó code áp quy tắc quyền hạn, kiểm tra đầu vào và điều phối script. Ngưỡng và loại intent sẽ cần thiết kế lại bằng dữ liệu thực tế; ý tưởng này không phải tính năng có sẵn của Shapeshift. `src/lib/jev/types.ts:84-97`, `src/lib/decide.ts:54-77`
- **Mức tin cậy vừa:** Preview, lựa chọn giữa hai ý định và quyền chọn tay phù hợp với tác vụ chưa rõ, vì chúng giữ quyết định cuối cùng cho người dùng khi confidence thấp. Chưa có nghiên cứu UX hay đo lỗi thao tác trong repo. `src/lib/decide.ts:54-77`, `src/lib/decide.ts:126-134`, `src/components/shapeshift/Shapeshift.tsx:226-244`

## Điểm mạnh

- **Typed contract xuyên online/offline:** một schema cho đầu ra, xác thực ở client và test kiểm tra ví dụ offline giúp fallback không đổi hình dạng dữ liệu. `src/lib/jev/types.ts:84-97`, `src/hooks/useIntent.ts:46-49`, `src/lib/__tests__/mock.test.ts:43-50`
- **Ổn định qua thời gian:** debounce, abort, stale-result guard, hysteresis cho ý định và tín hiệu phụ giải quyết loại lỗi hay gặp khi AI trả kết quả liên tục. `src/hooks/useIntent.ts:52-121`, `src/lib/decide.ts:80-124`, `src/lib/signals.ts:61-102`
- **Người dùng có đường sửa sai:** chips/palette có thể ép loại thẻ; raw text được giữ để mở lại và sửa. `src/lib/decide.ts:126-134`, `src/components/shapeshift/Shapeshift.tsx:157-168`, `src/components/shapeshift/Shapeshift.tsx:193-203`

## Điểm yếu và rủi ro

- **Privacy theo chế độ:** khi online, nguyên văn đầu vào gửi đến Jev qua server; route còn log tối đa 40 ký tự chuẩn hóa của đầu vào. Nội dung có thể là liên hệ, ghi chú hoặc khoản chi. Vì vậy “key không vào browser” không đồng nghĩa “nội dung luôn ở máy local”. `src/lib/jev/client.ts:47-50`, `src/app/api/intent/route.ts:27-30`, `src/lib/jev/types.ts:3-23`, `src/lib/savedItems.ts:4-10`
- **Offline classifier thiên về tiếng Anh và ví dụ cụ thể:** logic chứa regex từ khóa tiếng Anh, timezone alias và một số mẫu điện thoại/đơn vị; test chủ yếu dùng câu mẫu cố định. Không có bằng chứng nó phân loại tốt tiếng Việt hoặc dữ liệu ngoài tập ví dụ. `src/lib/jev/mock.ts:27-39`, `src/lib/jev/mock.ts:42-105`, `src/lib/__tests__/mock.test.ts:7-50`
- **Ngưỡng là hằng số chưa được hiệu chuẩn công khai:** 0,4/0,7/0,85 và hysteresis khác được hard-code; test kiểm tra hành vi quanh ngưỡng nhưng không đo calibration, tỷ lệ sai hoặc UX trong thực tế. `src/lib/decide.ts:9-18`, `src/lib/__tests__/decide.test.ts:15-32`, `src/lib/__tests__/decide.test.ts:34-64`
- **Mở rộng một intent cần sửa nhiều nơi:** type, question, parser, registry, mock và test. README hướng dẫn đúng chuỗi đó, nhưng thiếu một nguồn schema sinh tự động có thể làm các định nghĩa lệch nhau. `README.md:108-116`, `src/lib/jev/types.ts:3-26`, `src/lib/parse/index.ts:51-71`
- **Persistence cục bộ có giới hạn:** dữ liệu trong `localStorage`, lỗi ghi được nuốt và chỉ giữ trong bộ nhớ phiên hiện tại. Đây là lựa chọn hợp lý cho demo, nhưng chưa đủ cho workflow nhiều thiết bị hoặc audit. `src/lib/savedItems.ts:21-27`, `src/lib/savedItems.ts:52-59`

## Recommendations

1. **Thử một router nhỏ cho workflow AI** (chi phí thấp-vừa): định nghĩa enum tác vụ và schema đầu ra; chỉ dùng model để phân loại yêu cầu, còn script/agent thực thi quy tắc cụ thể. Giữ `none` hoặc `needs-clarification` khi mơ hồ; log loại tác vụ và nguồn quyết định, không log nguyên văn yêu cầu nhạy cảm. Thử trên tập câu tiếng Việt thật trước khi chọn ngưỡng. Cơ sở: `src/lib/jev/questions.ts:3-10`, `src/lib/jev/types.ts:84-97`, `src/app/api/intent/route.ts:27-30`.
2. **Thêm ổn định cho kết quả AI tương tác** (chi phí vừa): hủy việc cũ, kiểm tra request id, yêu cầu kết quả mới thắng nhiều lần trước khi đổi trạng thái; cho phép người dùng chọn tay và giữ lựa chọn đó qua sửa nhỏ. Chỉ dùng với luồng tương tác liên tục, không áp ngưỡng xác suất tùy tiện cho kết luận nghiên cứu. Cơ sở: `src/hooks/useIntent.ts:63-121`, `src/lib/decide.ts:84-128`.
3. **Kiểm tra bằng golden cases và lỗi đối kháng** (chi phí vừa): ghi cặp đầu vào/loại kỳ vọng, bao gồm câu mơ hồ, tiếng Việt, request nhiều ý và trường hợp “không đủ dữ liệu”; đo precision theo từng loại, tỷ lệ fallback và số lần đổi trạng thái. Test nguồn của dự án là mẫu cho hành vi, nhưng chưa thay thế eval theo ngữ cảnh của thư viện này. Cơ sở: `src/lib/__tests__/mock.test.ts:7-56`, `src/lib/__tests__/decide.test.ts:15-121`.
4. **Giữ tuyến offline có cùng contract** (chi phí vừa): dùng quy tắc cục bộ cho trường hợp đơn giản, chuyển sang model khi cần; phản hồi phải giữ cùng schema và ghi provenance (`online`/`offline`) để so sánh. Đánh đổi là phải bảo trì classifier hai đường. Cơ sở: `src/lib/jev/mock.ts:152-158`, `src/lib/jev/mock.ts:221-225`, `src/lib/jev/client.ts:54-75`.

## Quyết định áp dụng

**`experiment`**. Sao chép nguyên tắc phân công trách nhiệm và cơ chế ổn định, không sao chép UI/card hoặc các giá trị threshold. Một thử nghiệm đạt yêu cầu nếu định tuyến được yêu cầu thật của `repo-learning`, trả `needs-clarification` đúng lúc và không làm hành động ngoài ý định người dùng. Trước khi dùng trong production, cần eval riêng cho tiếng Việt, privacy policy cho nội dung gửi ra ngoài và đo tỷ lệ phân loại sai. `src/lib/jev/questions.ts:3-10`, `src/lib/decide.ts:9-18`, `src/lib/jev/mock.ts:27-39`, `src/app/api/intent/route.ts:27-30`

## Evidence map

| Nhận định | Nguồn |
|---|---|
| Danh mục intent và contract kết quả | `src/lib/jev/types.ts:3-26`, `src/lib/jev/types.ts:84-97` |
| 14 câu hỏi typed, model chỉ phân loại | `src/lib/jev/questions.ts:3-10`, `src/lib/jev/questions.ts:11-102`, `src/lib/jev/client.ts:47-75` |
| Fallback offline và stale-result guard | `src/lib/jev/client.ts:19-23`, `src/app/api/intent/route.ts:21-39`, `src/hooks/useIntent.ts:32-121` |
| Phân tích và tính toán bằng code | `src/lib/parse/index.ts:46-80`, `src/lib/parse/calc.ts:64-112` |
| State machine và override của người dùng | `src/lib/decide.ts:3-18`, `src/lib/decide.ts:54-134` |
| Hysteresis tín hiệu phụ | `src/lib/signals.ts:15-23`, `src/lib/signals.ts:61-102` |
| Test hành vi được định nghĩa, chưa chạy | `src/lib/__tests__/mock.test.ts:7-56`, `src/lib/__tests__/decide.test.ts:15-121`, `src/lib/__tests__/signals.test.ts:8-42` |
| Dữ liệu cục bộ và giới hạn privacy | `src/lib/savedItems.ts:4-27`, `src/lib/savedItems.ts:52-68`, `src/app/api/intent/route.ts:27-30` |

## Hạn chế của phân tích

- Chỉ đọc source, README, metadata Git và một số test tại HEAD nêu trên; không chạy code, cài dependency, thực thi script, benchmark hay thử Jev/API.
- Chưa kiểm tra UI/browser, latency, độ chính xác classifier online/offline hoặc mức phù hợp của 19 loại thẻ với người dùng thực tế.
- Chưa audit toàn bộ parser/card, dependency hay dịch vụ TypeSafe; nhận định bảo mật và privacy chỉ dựa trên các luồng mã đã đọc.
- Đây là snapshot của shallow clone. Commit mới, issue, release và hành vi deployment sau HEAD không thuộc phạm vi kết luận.
