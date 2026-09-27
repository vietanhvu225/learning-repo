# Repo Learning Library

Kho lưu trữ các phân tích về repository mã nguồn nhằm tìm ra ý tưởng, kỹ thuật và quy trình có thể áp dụng để cải thiện cách làm việc với AI.

Thư viện được thiết kế cho hai nhu cầu chính:

- Phân tích repository trên máy cá nhân, nơi có đầy đủ source code đã clone.
- Đồng bộ kết quả phân tích qua GitHub để có thể đọc lại trên máy khác mà không cần mang theo toàn bộ source code.

## Nguyên tắc tổ chức

1. Mỗi repository chỉ có một hồ sơ phân tích chính.
2. Source code đã clone và nội dung phân tích được lưu tách biệt.
3. Repository được phân loại bằng tag, không bị chia cứng theo category folder.
4. Mọi lần phân tích đều gắn với một commit cụ thể để tránh phân tích trùng và giúp kiểm chứng kết luận.
5. Các file kiến thức được commit lên GitHub; các repository nguồn trong `sources/` chỉ là cache cục bộ và không được push.
6. Không tự động xóa repository đã clone. Việc dọn source sẽ do người dùng quyết định.

## Cấu trúc thư mục

```text
repo-learning/
|
|-- README.md
|-- .gitignore
|
|-- sources/                         # Repo clone cục bộ; không push lên GitHub
|   |-- README.md
|   |-- github/
|   |   `-- owner/
|   |       `-- repository/
|   `-- gitlab/
|       `-- owner/
|           `-- repository/
|
|-- analyses/                        # Nội dung phân tích được version control
|   `-- github/
|       `-- owner--repository/
|           |-- README.md            # Bài phân tích chính
|           |-- implementation-notes.md
|           `-- assets/
|
|-- indexes/                         # Các góc nhìn được sinh từ metadata
|   |-- all-repositories.md
|   |-- by-tag/
|   |   |-- ai-agents.md
|   |   |-- context-management.md
|   |   `-- developer-workflow.md
|   `-- by-status/
|       |-- analyzed.md
|       |-- needs-review.md
|       `-- applied.md
|
|-- registry/
|   |-- repositories.yaml            # Nguồn dữ liệu chống phân tích trùng
|   `-- tags.yaml                    # Danh mục tag chuẩn
|
|-- templates/
|   `-- repository-analysis.md       # Mẫu báo cáo thống nhất
|
|-- repo_learning/                    # Công cụ deterministic của thư viện
|   |-- identity.py                  # Chuẩn hóa URL/path thành canonical ID
|   |-- metadata.py                  # Đọc frontmatter và registry
|   |-- validation.py                # Kiểm tra contract và portability
|   `-- indexes.py                   # Sinh các index từ registry
|
|-- tests/                            # Regression tests cho automation
`-- docs/superpowers/plans/           # Kế hoạch triển khai đã duyệt
```


## Những gì được đồng bộ qua GitHub

Được commit và push:

- `README.md`
- `analyses/`
- `indexes/`
- `registry/`
- `templates/`
- `repo_learning/`
- `tests/`
- `docs/`
- Tài liệu hướng dẫn bên trong `sources/`

Không được commit:

- Repository được clone bên dưới `sources/github/`, `sources/gitlab/` hoặc provider khác.
- File tạm, cache và output trung gian phát sinh trong lúc phân tích.

Nhờ vậy, máy ở công ty có thể pull thư viện để đọc mọi bài phân tích mà không cần tải toàn bộ repository nguồn. Khi cần kiểm chứng hoặc phân tích tiếp một repo, repo đó có thể được clone lại từ URL đã lưu trong registry.

## Luồng xử lý khi nhận URL

1. Chuẩn hóa URL về định danh dạng `provider/owner/repository`.
2. Kiểm tra định danh và canonical remote URL trong `registry/repositories.yaml`.
3. Nếu repo chưa tồn tại, clone vào `sources/<provider>/<owner>/<repository>/`.
4. Ghi nhận commit hiện tại của repo.
5. Phân tích theo template tại `templates/repository-analysis.md`.
6. Lưu kết quả vào `analyses/<provider>/<owner>--<repository>/README.md`.
7. Gắn tag bằng YAML frontmatter và cập nhật registry.
8. Sinh lại index tổng và các index theo tag/trạng thái.
9. Commit các file kiến thức để sẵn sàng push lên GitHub.

### Khi repo đã từng được phân tích

- Cùng canonical repo và cùng commit: không phân tích lại.
- Cùng repo nhưng commit mới: báo rằng source đã thay đổi; chỉ cập nhật phân tích khi được yêu cầu.
- URL khác nhưng trỏ về cùng canonical remote: xem là cùng một repo.
- Fork khác owner: mặc định xem là repo riêng, trừ khi được đánh dấu rõ là bản sao phục vụ cùng một phân tích.

### Canonical identity và aliases

Repository được định danh bằng `canonical_id` dạng `host/owner/repository`, không dùng hash của URL thô. Các dạng HTTPS, SSH, hậu tố `.git` và dấu `/` cuối được chuẩn hóa về cùng một identity.

`aliases` chỉ chứa những cách viết khác nhau của cùng một origin. URL upstream của một fork được lưu ở trường `upstream`; upstream không phải alias và vẫn là một repository độc lập nếu được phân tích riêng.

## Registry

`registry/repositories.yaml` là nguồn dữ liệu chính để xác định repo nào đã được xử lý.

Ví dụ:

```yaml
repositories:
  - id: github.com/owner/repository
    provider: github
    owner: owner
    repository: repository
    url: https://github.com/owner/repository
    source_path: sources/github/owner/repository
    analysis_path: analyses/github/owner--repository/README.md
    analyzed_commit: abc1234
    analyzed_at: 2026-09-28
    status: analyzed
    adoption: watch
    confidence: medium
    aliases: []
    upstream: null
    tags:
      - ai-agents
      - developer-workflow
```

## Metadata của bài phân tích

Mỗi bài phân tích bắt đầu bằng YAML frontmatter:

```yaml
---
repo: owner/repository
provider: github
canonical_id: github.com/owner/repository
url: https://github.com/owner/repository
aliases: []
upstream: null
analyzed_at: 2026-09-28
analyzed_commit: abc1234
analysis_version: 1
status: analyzed
adoption: watch
confidence: medium
tags:
  - ai-agents
  - context-management
  - developer-workflow
---
```

Nội dung chính viết bằng tiếng Việt và giữ nguyên thuật ngữ kỹ thuật tiếng Anh khi việc dịch thuật có thể làm mất nghĩa.

### Phân loại bằng chứng

Mỗi báo cáo phải tách rõ bốn loại nội dung:

- `Observed in code`: quan sát trực tiếp từ source, test hoặc Git metadata.
- `Claimed by project`: tuyên bố từ README, tài liệu hoặc benchmark chưa được xác minh độc lập.
- `Inferences`: suy luận của người phân tích dựa trên bằng chứng đã nêu.
- `Recommendations`: quyết định hoặc đề xuất áp dụng cho workflow.

Không dùng điểm confidence giả chính xác khi chưa có benchmark. Chỉ dùng `high`, `medium` hoặc `low` và giải thích giới hạn trong báo cáo.

## Hệ thống tag

Tag sử dụng mô hình lai:

- Ưu tiên tag chuẩn đã khai báo trong `registry/tags.yaml`.
- AI có thể đề xuất tag mới khi các tag hiện tại không diễn tả đúng nội dung.
- Tag mới cần có tên, mô tả và nguyên tắc sử dụng rõ ràng trước khi thêm vào danh mục chuẩn.
- Một repo có thể mang nhiều tag nhưng chỉ có một bài phân tích chính.

Category không phải là folder vật lý. Các trang trong `indexes/by-tag/` là góc nhìn được sinh từ tag, do đó một bài phân tích có thể xuất hiện trong nhiều category mà không bị sao chép.

## Trạng thái đề xuất

- `queued`: đã đăng ký nhưng chưa phân tích.
- `analyzing`: đang phân tích.
- `analyzed`: đã có báo cáo hoàn chỉnh.
- `needs-review`: cần người dùng xem hoặc xác nhận.
- `applied`: đã áp dụng ít nhất một ý tưởng vào workflow thực tế.
- `archived`: giữ lại lịch sử nhưng không còn ưu tiên theo dõi.

## Quyết định áp dụng

Mỗi báo cáo có một quyết định chính:

- `adopt-now`: đủ bằng chứng và phù hợp để áp dụng ngay.
- `experiment`: đáng thử trong phạm vi nhỏ trước khi chuẩn hóa.
- `watch`: có tiềm năng nhưng chưa đủ nhu cầu hoặc bằng chứng.
- `reject`: không phù hợp, rủi ro cao hoặc chi phí vượt lợi ích.

Các góc nhìn trong `indexes/by-adoption/` được sinh từ trường này.

## Automation deterministic

Skill hoặc AI agent chịu trách nhiệm đọc hiểu và tổng hợp. Các thao tác có thể xác định chính xác được giao cho package `repo_learning`:

- Chuẩn hóa URL/path và nhận diện repository trùng.
- Đọc YAML frontmatter và registry.
- Kiểm tra field bắt buộc, tag lạ, duplicate và link không portable.
- Sinh index theo tag, status và adoption decision.

Automation không tự chạy code, installer hay updater của repository được phân tích.

## Phạm vi của một bài phân tích

Một báo cáo nên trả lời tối thiểu:

1. Repo giải quyết vấn đề gì?
2. Điểm khác biệt hoặc ý tưởng đáng chú ý là gì?
3. Kiến trúc và luồng hoạt động chính ra sao?
4. Những kỹ thuật nào có thể áp dụng vào workflow làm việc với AI?
5. Lợi ích, chi phí và rủi ro khi áp dụng là gì?
6. Đề xuất cụ thể: áp dụng ngay, thử nghiệm, theo dõi thêm hay bỏ qua?
7. Những file hoặc commit nào là bằng chứng cho các kết luận quan trọng?

## Quy ước an toàn

- Không chạy script từ repo lạ trước khi kiểm tra mục đích và phạm vi ảnh hưởng.
- Không đưa secret, token, file môi trường hoặc dữ liệu cá nhân vào báo cáo hay Git history.
- Không sửa trực tiếp source repo chỉ để phục vụ việc phân tích.
- Mọi kết luận quan trọng nên dẫn tới file, symbol, tài liệu hoặc commit liên quan.
- Trước khi push, kiểm tra diff để chắc chắn chỉ có tri thức và công cụ của thư viện được commit.

## Hướng phát triển sau khi khởi tạo

1. Tạo cấu trúc folder và các file nền tảng.
2. Tạo template phân tích đầu tiên.
3. Tạo schema ban đầu cho registry và taxonomy tag.
4. Thử toàn bộ workflow với một repository mẫu.
5. Sau khi có correction thực tế, lưu lesson theo loại lỗi như `duplicate-repo`, `marketing-as-fact`, `stale-version`, `bad-tag` hoặc `unsafe-recommendation`.
6. Chuyển các lesson lặp lại thành eval có thể chạy lại; chưa thêm database hoặc vector search cho đến khi Markdown và `rg` không còn đáp ứng truy vấn thực tế.


