---
repo: vietanhvu225/watch-skill
provider: github
canonical_id: github.com/vietanhvu225/watch-skill
url: https://github.com/vietanhvu225/watch-skill
aliases:
  - https://github.com/vietanhvu225/watch-skill.git
  - git@github.com:vietanhvu225/watch-skill.git
upstream: https://github.com/oxbshw/watch-skill
analyzed_at: 2026-09-28
analyzed_commit: 264afc2bfe1bd4c11c8cac973f4b13016270c9a2
analysis_version: 1
status: analyzed
adoption: experiment
confidence: high
tags:
  - ai-agents
  - video-analysis
  - evidence-grounding
  - local-first
  - retrieval
  - agent-memory
  - evals
  - workflow-automation
---

# Phân tích `vietanhvu225/watch-skill`

## Kết luận ngắn

`watch-skill` là một **video-intelligence engine local-first dành cho AI agent**, không chỉ là một prompt/skill đơn lẻ. Nó biến URL, video local, stream hoặc screen recording thành frame đã chọn lọc, OCR, transcript và chỉ mục tìm kiếm; sau đó trả lời bằng bằng chứng có timestamp. Cùng engine còn có vòng lặp quan sát → phê bình → sửa → xác minh cho sản phẩm trực quan. Ba bề mặt MCP, CLI và REST chỉ là wrapper mỏng quanh core Python dùng chung, giúp hành vi không bị phân kỳ giữa các agent/harness. [Nguồn: `README.md`, dòng 15–23; `docs/architecture.md`, dòng 3–27]

Điều đáng học nhất cho `repo-learning` không phải phần xử lý video, mà là năm nguyên tắc:

1. **Analyze once, query many**: lưu kết quả thành memory có định danh ổn định, không phân tích lại vô ích.
2. **Evidence before prose**: mọi kết luận quan trọng phải trỏ về bằng chứng; khi thiếu bằng chứng thì từ chối kết luận.
3. **Cheap-first escalation**: quét tĩnh và truy xuất trước, chỉ đọc sâu hoặc dùng model mạnh khi tín hiệu chưa đủ.
4. **Correction becomes data**: phản hồi sai không chỉ sửa bài viết mà trở thành lesson và eval có thể chạy lại.
5. **Engine tách khỏi skill**: skill chỉ quyết định lúc nào/khi nào gọi công cụ; logic và persistence nằm trong engine/script có thể kiểm thử.

## Observed in code

Core Python, các surface mỏng, persistence, retrieval, confidence ladder và lesson workflow đều được quan sát trực tiếp trong source; các phần kiến trúc bên dưới dẫn tới file và dòng tương ứng.

## Claimed by project

Phiên bản package, trạng thái Beta, benchmark, số lượng test và chất lượng runtime là tuyên bố từ metadata hoặc tài liệu dự án; lượt phân tích này không chạy package để xác minh độc lập.

## Inferences

Khả năng áp dụng các pattern của dự án vào `repo-learning` là suy luận thiết kế dựa trên boundary, persistence và evidence contract đã quan sát, không phải tính năng có sẵn của dự án.

## Recommendations

Áp dụng canonical registry, evidence-first reporting, cheap-first escalation và generated indexes; thử nghiệm lessons/evals sau khi có correction thật; chưa dùng vector search ở quy mô hiện tại.

Không nên sao chép nguyên xi vault hiện tại. `video-learning-vault` có giá trị nội dung cao, nhưng index được duy trì thủ công, dùng link tuyệt đối gắn với ổ đĩa local, category đơn và metadata không thống nhất — không phù hợp cho việc đồng bộ giữa nhiều PC. [Nguồn: `video-learning-vault/index.md`, dòng 15–28, 110–150, 163–207; `video-learning-vault/ai-agents/shopify_claude_code_workflow.md`, dòng 1–9]

## Phạm vi và danh tính phiên bản

- Local source: checkout do người dùng cung cấp; path tuyệt đối được lược bỏ để báo cáo portable.
- Branch: `main`
- Commit: `264afc2bfe1bd4c11c8cac973f4b13016270c9a2`
- Commit date: `2026-09-27T23:18:53+07:00`
- Origin: `https://github.com/vietanhvu225/watch-skill.git`
- Upstream: `https://github.com/oxbshw/watch-skill`
- Working tree sạch tại thời điểm đọc.
- Package tự mô tả là phiên bản `1.0.0`, Python `>=3.11`, trạng thái Beta và MIT. [Nguồn: `pyproject.toml`, dòng 5–21]

Thông tin Git ở trên được lấy bằng `git remote -v`, `git rev-parse HEAD`, `git status --short` và `git show -s` tại thời điểm phân tích. Local ref `upstream/main` đang ở `958b30c…`; fork hiện chứa thêm rất nhiều thay đổi sản phẩm và toàn bộ `video-learning-vault`, nên báo cáo này mô tả **fork tại commit nêu trên**, không mặc định đại diện cho upstream mới nhất.

## Repo làm gì

Ba năng lực chính được thiết kế thành một hệ thống thống nhất:

- **Watch**: thu nhận video, phát hiện scene, chọn frame khác biệt, OCR và transcript.
- **Remember**: lưu transcript/frame/OCR/embedding vào index để tìm lại trong và giữa nhiều video.
- **Verify**: ghi lại hoạt động browser/screen, chấm theo tiêu chí ngôn ngữ tự nhiên, hướng dẫn sửa và tạo bằng chứng before/after. [Nguồn: `README.md`, dòng 33–39]

Các interface (skills, MCP, CLI, REST và adapter framework) dùng chung Python core. Quy tắc kiến trúc quan trọng là core không import `surfaces/`; surface chỉ render, core tính toán. [Nguồn: `README.md`, dòng 192–210; `docs/architecture.md`, dòng 3–27]

Repo cũng chứa một vault riêng của fork với bài phân tích và transcript video về AI agents, certification và workflow. Master index hiện cung cấp ít nhất ba góc nhìn: timeline, category và thời lượng học. [Nguồn: `video-learning-vault/index.md`, dòng 1–18, 110–112, 163–207]

## Kiến trúc và luồng xử lý video

```text
Skill / MCP / CLI / REST
          ↓
       acquire
          ↓
       perceive ──→ frames + OCR
          ↓
      transcribe ─→ captions / local Whisper / cloud opt-in
          ↓
        index ─────→ SQLite + FTS + embeddings
          ↓
 retrieve → confidence → local escalation → model verify → honest floor
          ↓
  answers / extraction / cross-video library / lessons
```

### 1. Acquire

Nguồn local được dùng trực tiếp; URL đi qua cache rồi fallback `yt-dlp → Cobalt nếu cấu hình → ffmpeg`. Hệ thống không thử vượt login/cookie và trả structured error nếu cả chuỗi thất bại. [Nguồn: `src/watch_skill/acquire/resolver.py`, dòng 25–45, 48–109, 112–148]

Có fast path `transcript_only`: thử lấy caption mà không tải video; nếu không có caption mới tải audio cho Whisper. [Nguồn: `src/watch_skill/watch.py`, dòng 77–99]

### 2. Perceive

Pipeline gọi `perceive()` sau khi probe metadata, truyền window, frame budget, cue timestamps và ngôn ngữ OCR. Perception bị bỏ qua hoàn toàn ở chế độ transcript-only. [Nguồn: `src/watch_skill/watch.py`, dòng 101–125]

Thiết kế được tài liệu hóa là scene detection → frame budget theo thời lượng → perceptual-hash dedup → OCR; focused mode tăng mật độ trong một window cụ thể. [Nguồn: `docs/architecture.md`, dòng 42–48]

### 3. Transcribe

Thứ tự là caption có sẵn → local Whisper → cloud STT opt-in. Mỗi nấc có thể thất bại mà pipeline vẫn tiếp tục; nếu không còn nguồn transcript, kết quả `source="none"` cho phép phân tích chỉ bằng frame. [Nguồn: `src/watch_skill/transcribe/ladder.py`, dòng 1–7, 20–71]

### 4. Index và memory

Kết quả được ghi vào SQLite gồm video, transcript segments, scenes, OCR, embeddings và FTS; retrieval kết hợp keyword và vector. [Nguồn: `docs/architecture.md`, dòng 56–63]

`index_watch_result()` persist frame, derived rows và text index, rồi distill notes theo kiểu best-effort. Khi answer cần nhìn kỹ hơn, `augment_video()` thêm frame/OCR mới vào index thay vì vứt bỏ tri thức cũ. [Nguồn: `src/watch_skill/index/store.py`, dòng 177–216]

### 5. Answer có kiểm chứng

Luồng trả lời là retrieval → confidence → resample/re-OCR cục bộ → vision verify nếu cần → honest floor. Prompt verify giới hạn model ở evidence đã index, yêu cầu JSON `supported/certainty/answer`, và timestamp do model tạo bị lọc nếu không nằm gần timestamp hợp lệ trong evidence. [Nguồn: `src/watch_skill/answer/engine.py`, dòng 1–6, 41–81, 135–168]

Confidence không phải “cảm giác” của model: nó trộn top score, margin với đối thủ, agreement giữa các loại evidence và lexical grounding. Trọng số hiện tại lần lượt là 0.25, 0.30, 0.15 và 0.30; zero lexical grounding bị chặn dưới floor trừ khi verify pass xác nhận. [Nguồn: `src/watch_skill/answer/confidence.py`, dòng 1–11, 31–49, 83–122; `src/watch_skill/answer/engine.py`, dòng 58–66]

Ngưỡng mặc định là floor `0.35`, target `0.6`, budget `8000` token; semantic answer cache coi cosine similarity `0.92` là câu hỏi lặp. Lessons được giới hạn 300 token và tổng 500 bản ghi. [Nguồn: `src/watch_skill/config.py`, dòng 151–201]

### 6. Self-improvement và visual loop

Một correction được phân loại, embed, lưu cùng guidance; với lỗi cơ học như OCR/timestamp/sampling, câu hỏi được chạy lại và lesson chỉ được đánh dấu validated khi đủ từ khóa correction xuất hiện trong answer/evidence. [Nguồn: `src/watch_skill/lessons/report.py`, dòng 17–18, 23–70, 73–96]

Vòng lặp visual tách vai trò rõ: hệ thống capture và critic, còn agent sửa code; iteration tiếp theo recapture, re-critique và diff, dừng khi pass, quá số vòng hoặc không tiến bộ. [Nguồn: `docs/architecture.md`, dòng 165–177]

## Thiết kế skill và prompt

Repo dùng một skill tổng `watch` và nhiều skill theo ý định cụ thể. `watch` là wrapper mỏng quanh CLI; engine không biết agent nào đang gọi nó. [Nguồn: `adapters/claude-skill/skills/watch/SKILL.md`, dòng 11–21; `docs/architecture.md`, dòng 219–222]

Các cơ chế prompt đáng học:

- **Trigger giàu ví dụ đầu vào**: `watching-videos` liệt kê URL, TikTok, stream, local video, screen/meeting recording để tăng recall, đồng thời mô tả hành động cụ thể. [Nguồn: `adapters/claude-skill/skills/watching-videos/SKILL.md`, dòng 1–16]
- **Precondition rõ**: trước khi xử lý, chạy `list`; nếu đã có thì `ask`, không watch lại. [Nguồn: `adapters/claude-skill/skills/watching-videos/SKILL.md`, dòng 18–30]
- **Progressive workflow**: transcript-only cho câu hỏi chỉ cần lời nói; focused window cho đoạn cụ thể; batch cho playlist/folder. [Nguồn: `adapters/claude-skill/skills/watching-videos/SKILL.md`, dòng 32–58]
- **Contract chống hallucination**: cite timestamp, tin vào refusal, chỉ đọc frame khi engine yêu cầu. [Nguồn: `adapters/claude-skill/skills/asking-with-evidence/SKILL.md`, dòng 10–34]
- **Tách use case khỏi implementation**: `video-memory` phân biệt locate (`search`) với cross-video synthesis (`library ask`). [Nguồn: `adapters/claude-skill/skills/video-memory/SKILL.md`, dòng 27–59]
- **Correction có hành động bắt buộc**: khi user sửa, gọi `lessons add`, không chỉ xin lỗi. [Nguồn: `adapters/claude-skill/skills/learning-from-mistakes/SKILL.md`, dòng 10–29]
- **Silent success, actionable failure**: preflight thành công thì không làm phiền; lỗi trả fix và chỉ hỏi user sau một lần remediation. [Nguồn: `adapters/claude-skill/skills/watch/SKILL.md`, dòng 23–35]

## Điểm mạnh đáng học

### 1. Artifact và provenance là trung tâm

Output được thiết kế để tồn tại ngoài phiên chat: database, cached answer, lesson, eval, viewer HTML và vault Markdown. Đây là hướng phù hợp trực tiếp với mục tiêu dùng PC nhà để phân tích và PC công ty để đọc.

### 2. “Honest floor” được enforce bằng code

Đây không chỉ là lời nhắc trong prompt. Engine tự tính confidence, chạy escalation có giới hạn, nhận rejection của vision model và chọn nội dung từ chối khi confidence dưới floor hoặc thiếu evidence. [Nguồn: `src/watch_skill/answer/engine.py`, dòng 201–308]

### 3. Chi phí được quản lý bằng thứ tự công việc

Model-free retrieval và local remediation chạy trước; model call chỉ dùng khi cần, có budget và cache. Đây là pattern tốt cho phân tích repo: `rg`/manifest/tree/tests trước, LLM synthesis sâu sau. [Nguồn: `docs/architecture.md`, dòng 120–148]

### 4. Lỗi trở thành regression asset

Lesson có classification, validation và eval replay, thay vì chỉ tích lũy “mẹo” không đo được. [Nguồn: `docs/architecture.md`, dòng 150–163]

### 5. Structured errors thân thiện với agent

Error có stable code, message, fix và details, tránh bắt agent parse prose. [Nguồn: `docs/architecture.md`, dòng 69–79]

### 6. Boundary core/surface tốt

Một core dùng cho CLI/MCP/REST/framework adapters giảm trùng logic và làm automation lâu dài dễ bảo trì hơn. [Nguồn: `docs/architecture.md`, dòng 3–27, 196–222]

## Điểm yếu và rủi ro

### 1. Chống trùng chỉ dựa trên chuỗi source thô

`video_id_for()` hash `source.strip()`, nên URL alias, short URL, tracking query hoặc cùng video qua URL khác có thể thành các video khác nhau. [Nguồn: `src/watch_skill/index/store.py`, dòng 16–18]

**Bài học cho repo-learning:** canonicalize Git remote (`host/owner/repo`, bỏ `.git`, normalize case phù hợp host) và lưu aliases; không hash nguyên URL user gửi.

### 2. Vault Markdown chưa portable và khó sinh tự động

Index chứa link tuyệt đối gắn với checkout local, nên link sẽ hỏng trên PC công ty hoặc khi checkout ở path khác. Bài viết dùng bullet metadata tự do thay vì YAML frontmatter; master index phải lặp lại nội dung theo timeline/category/duration. [Nguồn: `video-learning-vault/index.md`, dòng 18–28, 110–150, 163–207; `video-learning-vault/ai-agents/shopify_claude_code_workflow.md`, dòng 1–9]

**Bài học:** dùng relative Markdown links, YAML frontmatter chuẩn, và generate index từ metadata; tuyệt đối không sửa index thủ công.

### 3. Một số claim trong vault là diễn giải bậc hai

Các bài vault tóm tắt lời người nói trong video; ví dụ bài Shopify đưa ra các tuyên bố rất mạnh và recommendation riêng. Chúng hữu ích để khám phá ý tưởng nhưng không đồng nghĩa đã kiểm chứng với source code/tài liệu gốc của Shopify. [Nguồn: `video-learning-vault/ai-agents/shopify_claude_code_workflow.md`, dòng 13–25, 80–116]

**Bài học:** báo cáo repo nên tách `Observed in code`, `Claimed by project`, `Inference`, `Recommendation` để tránh biến marketing hoặc lời kể thành fact.

### 4. Confidence vẫn là heuristic cục bộ

Trọng số confidence được hard-code và calibration mô tả chỉ dựa trên một số run cụ thể; repo ghi nhận benchmark trên một máy Windows 10, RAM 8 GB và 202 tests tại thời điểm tài liệu. Điều này chưa chứng minh calibration tổng quát cho mọi ngôn ngữ/video. [Nguồn: `src/watch_skill/answer/confidence.py`, dòng 19–24, 109–122; `docs/DECISIONS.md`, dòng 170–210]

**Bài học:** repo-learning không nên gắn “confidence 0.83” nếu chưa có dataset; dùng mức `high/medium/low` gắn với loại evidence và ghi rõ lý do.

### 5. “Local-first” không có nghĩa mọi dữ liệu đều ở local

Cloud vision request base64-encode và gửi các extracted frames cùng prompt cho Anthropic/OpenAI/OpenRouter/Gemini khi provider tương ứng được cấu hình. Chỉ Ollama hoàn toàn local. [Nguồn: `src/watch_skill/vision/client.py`, dòng 34–78, 85–101, 109–140, 164–183]

**Rủi ro:** screen recording có thể chứa secret/PII. Cần policy nói rõ “video file không upload” khác với “không có frame/audio nào rời máy”.

### 6. Self-healing có supply-chain surface

Khi phát hiện extractor breakage, code tự update `yt-dlp` rồi retry; skill doctor cũng được hướng dẫn auto-bootstrap binaries. [Nguồn: `src/watch_skill/acquire/ytdlp.py`, dòng 188–208; `adapters/claude-skill/skills/watch/SKILL.md`, dòng 23–35]

**Rủi ro:** tiện lợi nhưng mutation ẩn và tải executable mới. Trong workflow repo-learning, update/install phải là bước rõ ràng cần approval; phân tích repo mặc định chỉ read-only.

### 7. Auto-update bài phân tích có thể xóa derived state

Khi re-index cùng ID, code xóa segments/scenes/OCR/embeddings/answers cũ rồi ghi lại. [Nguồn: `src/watch_skill/index/store.py`, dòng 35–59]

**Bài học:** với báo cáo repo, không overwrite không dấu vết; lưu `analyzed_commit`, changelog ngắn và có thể giữ history trong Git.

### 8. Báo cáo này chưa xác minh runtime

Theo phạm vi an toàn, không chạy code repo, không cài dependency và không chạy test. Vì vậy các tuyên bố về hiệu năng, số integration hoạt động, chất lượng OCR/transcription và test pass chỉ được ghi nhận như claim/tài liệu của repo, không được xác nhận độc lập.

## Áp dụng cụ thể vào `repo-learning`

### A. Metadata schema bắt buộc

Mỗi `analyses/<host>/<owner>--<repo>/README.md` nên có frontmatter:

```yaml
repo: owner/repo
canonical_id: github.com/owner/repo
url: https://github.com/owner/repo
aliases: []
analyzed_commit: <sha>
analyzed_at: <date>
analysis_version: 1
status: analyzed
tags: []
confidence: high
```

Đây là bản tương đương repo của `video_id + index`, nhưng canonical ID phải dựa trên remote chuẩn hóa thay vì raw URL.

### B. Pipeline phân tích dạng ladder

1. **Registry check**: canonicalize URL/path, kiểm tra commit đã phân tích.
2. **Cheap static pass**: README, manifest, tree, entry points, tests, docs/ADR, license, git metadata.
3. **Focused pass**: chỉ mở module liên quan câu hỏi/mục tiêu của user.
4. **Evidence synthesis**: mọi claim quan trọng cite `path:Lx-Ly`; đánh nhãn `observed`, `claimed`, `inferred`.
5. **Challenge pass**: tìm claim không được code/test hỗ trợ, rủi ro security/privacy/maintenance.
6. **Adoption decision**: `adopt-now`, `experiment`, `watch`, hoặc `reject`, kèm lý do và effort.
7. **Persist**: ghi đúng một report, update registry rồi regenerate index/tag views.

### C. Template báo cáo nên học từ evidence contract

Các section cố định nên là:

- `Kết luận ngắn`
- `Repo làm gì`
- `Kiến trúc/luồng chính`
- `Cơ chế đáng học`
- `Điểm mạnh`
- `Điểm yếu/rủi ro`
- `Ý tưởng áp dụng`
- `Quyết định: adopt / experiment / watch / reject`
- `Evidence map`
- `Limitations`

### D. Tag thay folder category

Vault hiện lặp cùng bài trong timeline/category/duration. `repo-learning` nên giữ mỗi repo đúng một analysis, rồi generate:

- `indexes/all-repositories.md`
- `indexes/by-tag/<tag>.md`
- `indexes/by-status/<status>.md`
- tùy chọn `indexes/by-adoption/<decision>.md`

Tag nên là controlled vocabulary nhưng AI được đề xuất tag mới; generator báo tag lạ để user duyệt.

### E. Lessons và evals cho chính workflow phân tích repo

Tạo `registry/lessons.yaml` hoặc `lessons/*.md`, mỗi correction gồm:

- loại lỗi: `missed-file`, `marketing-as-fact`, `stale-version`, `wrong-architecture`, `duplicate-repo`, `bad-tag`, `unsafe-recommendation`;
- báo cáo/claim sai;
- correction;
- guidance;
- validation case.

Từ đó tạo eval tối thiểu:

- nhận ra cùng repo từ HTTPS/SSH/`.git` URL;
- không phân tích lại cùng commit;
- phân biệt origin fork với upstream;
- mọi recommendation phải có evidence hoặc ghi là inference;
- link nội bộ là relative, không chứa drive letter;
- report không chứa secret từ `.env`;
- unknown tag bị validator phát hiện.

### F. Tách engine khỏi orchestration skill

Nên có các script deterministic cho canonicalize/registry/index/validate, còn skill chỉ điều phối:

```text
skill: when + why + safety + decision rules
scripts: clone/check SHA/register/generate indexes/validate links
agent: đọc hiểu code, tổng hợp evidence, đánh giá adoption
```

Đây là bản sao chép đúng tinh thần `watch-skill`: “surface quyết định lúc dùng; core chịu trách nhiệm logic”. [Nguồn: `docs/architecture.md`, dòng 3–27, 219–222]

## Ưu tiên triển khai đề xuất

### P0 — nên làm ngay

1. Chuẩn hóa YAML frontmatter và relative links.
2. Registry canonical ID + aliases + analyzed commit.
3. Generator index từ metadata; không edit index thủ công.
4. Template bắt buộc phân biệt `Observed / Claimed / Inferred`.
5. Validator kiểm tra duplicate, link tuyệt đối, missing SHA và tag lạ.

### P1 — sau khi đã phân tích 5–10 repo

1. Tạo tag views và adoption views.
2. Ghi lessons từ corrections thực tế.
3. Tạo eval cho duplicate detection và report quality.
4. Incremental refresh: diff commit mới với `analyzed_commit`, không mặc định phân tích lại toàn repo.

### P2 — chỉ khi thư viện đủ lớn

1. Full-text/vector search xuyên report.
2. Semantic cache cho câu hỏi lặp.
3. Cross-repo synthesis có citation.
4. Confidence/escalation tự động dựa trên benchmark riêng.

Không nên bắt đầu bằng SQLite/vector DB: với vài chục repo, Markdown + YAML + generated indexes + `rg` dễ kiểm tra, portable và đủ mạnh. Hãy chỉ thêm database khi truy vấn thực tế chứng minh Markdown không đáp ứng.

## Quyết định áp dụng

| Cơ chế | Quyết định | Lý do |
|---|---|---|
| Core tách surface/skill | **Adopt now** | Giảm trùng logic, dễ test và dùng từ nhiều agent |
| Persistent registry + analyze once | **Adopt now** | Đúng mục tiêu chống phân tích trùng |
| Evidence + honest floor | **Adopt now** | Nâng độ tin cậy báo cáo |
| Generated multi-view indexes | **Adopt now** | Thay thế category folder cứng và index thủ công |
| Lessons → replayable evals | **Experiment** | Rất có giá trị sau khi có correction thật |
| Cheap-first escalation | **Adopt now** | Giảm context/token và thời gian |
| SQLite/FTS/vector search | **Watch** | Chưa cần cho thư viện nhỏ |
| Auto-update/install binaries | **Reject for default workflow** | Không phù hợp chế độ phân tích read-only |
| Raw-source hash làm canonical ID | **Reject** | Không xử lý alias/fork/upstream tốt |

## Evidence map nhanh

| Chủ đề | Nguồn chính |
|---|---|
| Product scope | `README.md:15–23`, `README.md:33–39` |
| Core/surface boundary | `docs/architecture.md:3–27`, `docs/architecture.md:219–222` |
| Pipeline | `docs/architecture.md:29–67`, `src/watch_skill/watch.py:59–158` |
| Persistence/reuse | `src/watch_skill/index/store.py:16–18`, `src/watch_skill/index/store.py:177–216` |
| Evidence/confidence/refusal | `src/watch_skill/answer/engine.py:41–81`, `src/watch_skill/answer/engine.py:201–342` |
| Lessons | `src/watch_skill/lessons/report.py:23–96` |
| Skill orchestration | `adapters/claude-skill/skills/watch/SKILL.md:23–124` |
| Vault organization | `video-learning-vault/index.md:12–207` |
| Portability problem | `video-learning-vault/index.md:18–28`, `video-learning-vault/ai-agents/shopify_claude_code_workflow.md:1–9` |
| Cloud-frame privacy boundary | `src/watch_skill/vision/client.py:34–101`, `src/watch_skill/vision/client.py:164–183` |

## Hạn chế của phân tích

- Chỉ dùng source code, tài liệu và Git metadata local tại commit đã ghi; không browse upstream/GitHub để kiểm tra trạng thái mới hơn.
- Không chạy package, test, benchmark, installer hay network call.
- Không đọc `.env`; file này được ignore theo `.gitignore` dòng 12–19.
- Không đánh giá chất lượng thực tế của model/OCR/transcription trên video mẫu.
- Một phần tài liệu trong fork có ngày tương lai theo clock hiện tại của workspace; báo cáo giữ nguyên metadata Git và không suy đoán thêm.
