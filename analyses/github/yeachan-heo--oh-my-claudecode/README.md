---
repo: yeachan-heo/oh-my-claudecode
provider: github
canonical_id: github.com/yeachan-heo/oh-my-claudecode
url: https://github.com/yeachan-heo/oh-my-claudecode
aliases:
  - https://github.com/Yeachan-Heo/oh-my-claudecode.git
  - git@github.com:Yeachan-Heo/oh-my-claudecode.git
upstream: null
analyzed_at: 2026-09-29
analyzed_commit: 9fd35ece5d6de65b511bf43b55e42c499e4fc194
analysis_version: 1
status: analyzed
adoption: experiment
confidence: medium
tags:
  - ai-agents
  - workflow-automation
  - agent-memory
  - evidence-grounding
  - evals
---

# Phân tích `yeachan-heo/oh-my-claudecode`

## Kết luận ngắn

`oh-my-claudecode` (OMC) là tầng điều phối nhiều agent cho Claude Code, có plugin trong phiên làm việc và CLI Node.js riêng. Điều đáng thử cho workflow kỹ thuật có AI là **hợp đồng chuyển giai đoạn có bằng chứng**, checkpoint gắn với quyền sở hữu task, và prompt được sinh từ một nguồn có digest. Không nên nhập cả runtime vào `repo-learning`: hook và slash skill phụ thuộc Claude Code, terminal team cần tmux, trong khi named autopilot profile chỉ hỗ trợ Linux. Đây là đánh giá cấu trúc từ mã và tài liệu, chưa phải xác nhận hiệu năng khi chạy. [`package.json:2-20`, `hooks/hooks.json:3-28`, `README.md:128-130`, `README.md:148-157`, `README.md:599-610`]

## Repo làm gì

Package công bố bản `5.5.0`, các lệnh `oh-my-claudecode`/`omc`, Node `20.x` hoặc `22.x`–`26.x` (không gồm `21.x`), và phụ thuộc Claude Agent SDK, MCP SDK cùng `better-sqlite3`. Plugin đưa vào Claude Code các hook, skill và agent; CLI có bề mặt terminal riêng. Cặp `/team` và `omc team` là **hai runtime khác nhau**, không nên coi là một API tương đương. [`package.json:2-20`, `package.json:92-104`, `package.json:122-124`, `README.md:139-157`, `README.md:171-177`]

## Kiến trúc và luồng chính

Tài liệu dự án mô tả đường đi `user input → hooks → skills → agents → state`. Manifest hook thực sự đăng ký các điểm `UserPromptSubmit`, `SessionStart`, `PreToolUse`, `PostToolUse`, `PreCompact`, `Stop` và vòng đời subagent. `team` được mô tả theo `plan → PRD → exec → verify → fix`; mã state khởi tạo ở `team-plan`, lưu phase history, chặn vòng sửa sau số lần tối đa và đặt terminal `failed`. [`docs/ARCHITECTURE.md:9-11`, `docs/ARCHITECTURE.md:43-47`, `hooks/hooks.json:3-28`, `hooks/hooks.json:87-108`, `hooks/hooks.json:126-193`, `skills/team/SKILL.md:120-151`, `src/hooks/team-pipeline/state.ts:69-110`, `src/hooks/team-pipeline/state.ts:158-222`]

## Observed in code

- **Điều phối và lifecycle.** Team state gắn `session_id`, phase, artifact paths, worker/task counts, fix attempts và yêu cầu hủy; transition cùng phase là idempotent, riêng `team-fix` tăng attempt. Runtime đưa worker lệnh `claim-task` rồi `transition-task-status`, yêu cầu summary và verification khi hoàn thành. [`src/hooks/team-pipeline/state.ts:69-110`, `src/hooks/team-pipeline/state.ts:158-222`, `src/team/runtime-v2.ts:962-1000`]
- **Registry cho mode/skill/command.** `WorkflowEntry` ghi `kind`, quyết định `keep`/`merge`/`alias-deprecate`/`delete`, risk class, owner và target. Projection sắp xếp deterministic, tính SHA-256, kiểm tra skill/command đã cài có entry và entry không `declaredOnly` có file. Mã hiện khai báo sáu skill Tier-0; lời chú thích đầu file vẫn nói bốn, một dấu hiệu drift tài liệu nội bộ. [`src/workflow/registry.ts:97-132`, `src/workflow/registry.ts:143-155`, `src/workflow/projections.ts:86-106`, `src/workflow/projections.ts:118-176`, `src/workflow/registry.ts:1-9`]
- **Quản lý prompt/context.** Composer chọn section bắt buộc và overlay theo provider/model tier, sắp xếp, chuẩn hóa rồi gắn digest vào projection. Nội dung file được đánh dấu untrusted; sanitizer cắt độ dài và escape một tập delimiter. Prompt gửi external CLI có header ngăn đệ quy subagent; context path check loại control character và traversal theo path lexical, nhưng có tùy chọn `allowExternal`, nên đây không phải chứng minh mọi đường đọc file đều được cách ly. [`src/agents/prompt-ssot/compose.ts:24-105`, `src/agents/prompt-helpers.ts:195-234`, `src/mcp/prompt-injection.ts:44-109`]
- **Persistence/recovery.** Checkpoint task tối đa 64 KiB, hash payload JSON canonical, ràng buộc team/task/worker/version/claim token trước khi công bố; replay giống hệt được chấp nhận, xung đột bị từ chối. Khi chọn để resume, mã chỉ nhận checkpoint hợp owner/version/token và sequence cao nhất duy nhất. [`src/team/task-recovery-checkpoint.ts:9-29`, `src/team/task-recovery-checkpoint.ts:31-68`, `src/team/task-recovery-checkpoint.ts:164-218`, `src/team/task-recovery-checkpoint.ts:221-244`]
- **Verification.** Tier selector nâng thay đổi security/architecture hoặc trên 20 file lên `THOROUGH`; thay đổi nhỏ có coverage đầy đủ được `LIGHT`, còn lại `STANDARD`. Test có ca cho các nhánh này. Đây là chính sách chọn độ sâu review, không phải bằng chứng rằng mỗi workflow đều đã chạy test/build thành công. [`src/verification/tier-selector.ts:8-60`, `src/verification/tier-selector.test.ts:11-86`]
- **Bảo mật mặc định.** Cấu hình mặc định tắt hạn chế đường dẫn tool, Python sandbox, chặn project skills, chặn auto-update, remote MCP và external LLM; `OMC_SECURITY=strict` bật chúng, với file config chỉ được siết thêm trong strict mode. Permission hook từ chối shell metacharacter ở các nhánh auto-approval thông thường, nhưng có ngoại lệ heredoc: chỉ cần command nhiều dòng, có heredoc marker và first line khớp prefix `git commit`/`git tag` an toàn; body không đi qua cùng bộ lọc metacharacter. Guard này không thay thế ranh giới quyền của host và cần test đối kháng trước khi bật auto-approval. [`src/lib/security-config.ts:22-56`, `src/lib/security-config.ts:88-119`, `src/hooks/permission-handler/index.ts:547-597`, `src/hooks/permission-handler/index.ts:640-675`]

## Claimed by project

- Dự án quảng bá “zero learning curve”, tự động hóa end-to-end và tiết kiệm 30–50% token nhờ routing. Các tuyên bố trải nghiệm/hiệu quả này **chưa được xác minh** bằng chạy benchmark hoặc so sánh độc lập trong lượt đọc này. [`README.md:17-26`, `README.md:284-293`]
- Tài liệu nói `/team` là bề mặt điều phối khuyến nghị, hỗ trợ luồng verify/fix và handoff 10–20 dòng lưu trong `.omc/handoffs/`; đây là hợp đồng hướng dẫn agent, chưa chứng minh mọi session tuân thủ. [`README.md:169-181`, `skills/team/SKILL.md:144-178`]
- Dự án nêu runtime state `.omc/` có thể chứa prompt, transcript và path máy; mặc định worktree-local, nên xóa worktree có thể làm mất state trừ khi dùng `OMC_STATE_DIR`. `.gitignore` của repo giữ `.omc/skills/` có thể commit, các phần `.omc/` khác bị ignore. Đây là chính sách trong repo, không phải đảm bảo privacy cho mọi host/provider. [`README.md:365-373`, `.gitignore:4-7`]
- README ghi named autopilot profiles cần Linux + `flock`, CLI team và rate-limit detection cần tmux/psmux; `/autopilot`, `/ralph`, `/execute`, `/team` là skill trong phiên Claude Code, không phải subcommand terminal tương ứng. Chưa chạy trên Windows hay các harness khác để xác minh compatibility. [`README.md:128-132`, `README.md:139-157`, `README.md:595-610`]

## Inferences

- **Mức tin cậy cao:** stage state, bounded fix loop và checkpoint có claim token là mẫu có thể chuyển sang bất kỳ harness nào nếu tách khỏi hook/CLI riêng của Claude. Chúng giảm nguy cơ report thành công khi state cũ hoặc worker khác được dùng lại; lợi ích thực tế vẫn cần fault-injection test. [`src/hooks/team-pipeline/state.ts:158-222`, `src/team/task-recovery-checkpoint.ts:178-218`, `src/team/task-recovery-checkpoint.ts:221-244`]
- **Mức tin cậy vừa:** prompt SSOT + digest và registry drift check có thể chống lệch giữa tài liệu, skill và bề mặt cài đặt; chính file registry cho thấy comment và entries đã lệch về số Tier-0, nên cơ chế cần bao phủ cả mô tả prose. [`src/agents/prompt-ssot/compose.ts:31-105`, `src/workflow/projections.ts:145-176`, `src/workflow/registry.ts:1-9`, `src/workflow/registry.ts:143-155`]
- **Mức tin cậy vừa:** local state giúp resume nhưng tăng bề mặt lưu dữ liệu nhạy cảm và rủi ro mất state theo vòng đời worktree. Cần phân loại artifact, retention và chọn state root trước khi áp dụng cho workflow chứa prompt hoặc transcript. [`README.md:365-373`, `src/lib/worktree-paths.ts:339-363`]

## Điểm mạnh

Hợp đồng stage/verify/fix có terminal failure rõ ràng; checkpoint chống replay xung đột theo claim; prompt projection có nguồn và digest; policy verification tăng theo mức rủi ro. Các cơ chế này có vị trí trong source và test, nên là phần đáng học hơn các khẩu hiệu sản phẩm. [`src/hooks/team-pipeline/state.ts:158-222`, `src/team/task-recovery-checkpoint.ts:178-244`, `src/agents/prompt-ssot/compose.ts:70-105`, `src/verification/tier-selector.test.ts:11-86`]

## Điểm yếu và rủi ro

- **Portability:** hook/skill trong phiên gắn Claude Code; CLI team cần tmux và CLI provider đã cài/auth; named profile Linux-only. Chuyển nguyên runtime sang Codex hay Windows native sẽ cần adapter và thử nghiệm riêng. [`hooks/hooks.json:3-28`, `README.md:148-157`, `README.md:195-226`, `README.md:128-130`, `README.md:599-610`]
- **Security/privacy:** default không bật các hạn chế quan trọng; external provider/MCP có thể được dùng tùy cấu hình. `.omc/` có thể giữ nội dung hội thoại và path, còn `.omc/skills/` được phép commit. Nhánh heredoc của auto-approval chỉ kiểm tra first-line prefix, nên pilot cần giữ permission flow hoặc có test đối kháng riêng thay vì suy ra toàn bộ body an toàn. Cần policy riêng trước khi cho workflow đụng dữ liệu nội bộ. [`src/lib/security-config.ts:39-56`, `src/hooks/permission-handler/index.ts:547-597`, `README.md:365-373`, `.gitignore:4-7`]
- **Chi phí và lỗi điều phối:** nhiều stage, agent, hook và state tạo overhead, race/recovery cases và chi phí model. Mã có fallback file lock khi native SQLite không có, cùng failure diagnostics; đó là dấu hiệu vận hành cần quan sát, chưa có số đo tin cậy từ lượt đọc này. [`hooks/hooks.json:3-28`, `src/lib/mode-state-io.ts:44-53`, `src/lib/mode-state-io.ts:269-308`, `src/team/task-recovery-checkpoint.ts:178-244`]

## Recommendations

1. **Adopt now ở mức pattern:** ghi stage, owner, exit criteria, handoff ngắn và evidence cho mỗi bước; giới hạn số vòng fix và có terminal `failed`. Thêm vào workflow phân tích repo bằng schema nhỏ, không cần plugin Claude. [`skills/team/SKILL.md:120-178`, `src/hooks/team-pipeline/state.ts:158-222`]
2. **Experiment:** tạo một pilot với hai worker trên task có thể lặp lại; đo thời gian, token, tỷ lệ task cần sửa, và thử worker chết giữa checkpoint/resume. Chỉ dùng dữ liệu không nhạy cảm, đặt state root/retention rõ ràng, bật strict policy và kiểm thử heredoc chứa shell metacharacter trước khi cho phép auto-approval. [`src/team/task-recovery-checkpoint.ts:164-244`, `src/lib/security-config.ts:39-56`, `src/hooks/permission-handler/index.ts:547-597`, `README.md:365-373`]
3. **Watch:** theo dõi prompt/registry drift gate và portability các adapter; không nhập bộ skill/hook hay auto-approval nguyên trạng vào `repo-learning` trước khi có hợp đồng quyền và test cross-harness. [`src/workflow/projections.ts:145-176`, `src/agents/prompt-ssot/compose.ts:70-105`, `src/hooks/permission-handler/index.ts:640-667`, `README.md:139-157`]

## Quyết định áp dụng

**`experiment`** cho runtime/multi-agent workflow; **adopt-now** cho mẫu stage gate, checkpoint ownership và evidence map; **watch** cho portability và registry/prompt projection; **reject** việc sao chép mặc định quyền/hook cùng lời hứa tiết kiệm token chưa kiểm chứng. Chi phí tích hợp và rủi ro privacy lớn hơn lợi ích của việc thay workflow hiện tại bằng OMC nguyên khối. [`README.md:128-157`, `src/lib/security-config.ts:39-56`, `src/team/task-recovery-checkpoint.ts:178-244`, `src/verification/tier-selector.ts:24-60`, `README.md:284-293`]

## Evidence map

| Nhận định | Nguồn chính |
|---|---|
| Bề mặt plugin, CLI và team khác runtime | `package.json:2-20`; `README.md:139-157` |
| Stage có fix loop và terminal failure | `src/hooks/team-pipeline/state.ts:69-110`; `src/hooks/team-pipeline/state.ts:158-222` |
| Checkpoint gắn claim/version và chống xung đột | `src/team/task-recovery-checkpoint.ts:164-244` |
| Prompt/skill projection có digest và drift check | `src/agents/prompt-ssot/compose.ts:31-105`; `src/workflow/projections.ts:145-176` |
| Security default và strict override | `src/lib/security-config.ts:39-56`; `src/lib/security-config.ts:88-119` |
| Ranh giới nền tảng và state privacy | `README.md:128-157`; `README.md:365-373`; `README.md:595-610` |

## Hạn chế của phân tích

Đã đọc source, test, tài liệu, manifest và Git metadata của shallow clone tại `main`/`9fd35ece5d6de65b511bf43b55e42c499e4fc194` (origin `https://github.com/Yeachan-Heo/oh-my-claudecode.git`; working tree sạch khi kiểm tra). Không cài dependency, chạy code/test/benchmark, đăng nhập provider, xem secret, hay xác minh hành vi thực tế và tuyên bố hiệu năng. Repo lớn và nhiều bề mặt, nên đánh giá là lấy mẫu theo những đường liên quan workflow kỹ thuật, không phải audit bảo mật toàn diện.
