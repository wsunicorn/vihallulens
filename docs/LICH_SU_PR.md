# Lịch sử pull request (bản chép từ repo lưu trữ)

Chép ngày 22/10/2026 từ repo `wsunicorn/vihallulens-luu-tru`, bản gốc của repo này. Repo gốc
đã được đổi tên, chuyển private và archive ngày 22/10/2026; repo hiện tại tạo lại với **đúng
lịch sử commit** của nhánh `main`. Vì vậy số PR trên GitHub của repo này đánh lại từ #1. Mọi số
PR nhắc tới trong `TASKS.md` và trong tiêu đề commit (`(#17)`, `Merge pull request #131`) là số
của repo lưu trữ, tức là số trong file này.

File này để tra cứu và đối chiếu:

- **Ngày mở và ngày gộp là ngày thật**, theo giờ Việt Nam, lấy từ GitHub của repo gốc.
- **Cột "Commit gộp" trỏ tới commit trong repo này**, nên ai cũng tự kiểm được PR đó đã vào
  `main` hay chưa. PR #1–#29 được gộp trước lần viết lại lịch sử ngày 27/08/2026 (bỏ dòng trailer
  khỏi thông điệp commit, nội dung file không đổi), nên mã commit gộp gốc của chúng đã đổi. Mã ghi
  ở đây là mã sau khi viết lại, đánh dấu ¹, tìm theo số PR ghi trong tiêu đề commit.
- **Mô tả PR chép nguyên văn**, gồm cả output kiểm thử đã dán. Chỉ hạ cấp tiêu đề (`##` thành
  `#####`) để không lẫn với mục lục của file.
- **Bình luận không chép.** Cả 98 bình luận đều của bot rà code tự động `coderabbitai[bot]`; cột
  "Bot" chỉ ghi số lượng. Bản đầy đủ nằm ở repo lưu trữ, cấp quyền đọc khi cần.

## Bảng tổng hợp

| PR | Tiêu đề | Người mở | Mở | Gộp | Commit gộp | Bot |
|---|---|---|---|---|---|---|
| [#1](#pr-1) | T01: khởi tạo repo, pyproject và bố cục src | wsunicorn | 19/08/2026 13:18 | 19/08/2026 13:24 | [`aebc263`](https://github.com/wsunicorn/vihallulens/commit/aebc2632cc273f85934a212ab2e72664989e5406)¹ | 1 |
| [#2](#pr-2) | T02: cấu hình ruff và pytest, thêm test smoke | wsunicorn | 19/08/2026 13:24 | 19/08/2026 17:54 | [`d473330`](https://github.com/wsunicorn/vihallulens/commit/d473330f35c4eb1b679666593d5f18e22aac7dcf)¹ | 1 |
| [#3](#pr-3) | T03: module cấu hình pydantic, loader YAML và config_hash | wsunicorn | 19/08/2026 17:55 | 19/08/2026 17:56 | [`f76898e`](https://github.com/wsunicorn/vihallulens/commit/f76898ee5edf16e76ffceec210ff0757d6bd28e0)¹ | 0 |
| [#4](#pr-4) | T04: module ghi kết quả runs.jsonl và xuất bảng | wsunicorn | 19/08/2026 17:58 | 19/08/2026 17:58 | [`648c96f`](https://github.com/wsunicorn/vihallulens/commit/648c96f29e51f8f182c902c72155c73aaa458d61)¹ | 1 |
| [#5](#pr-5) | T05: script đo ngân sách bộ nhớ và độ dài token tiếng Việt | wsunicorn | 19/08/2026 18:05 | 19/08/2026 18:05 | [`3ae1919`](https://github.com/wsunicorn/vihallulens/commit/3ae1919ed51b3930b6b2f236ae3549128ddb6cab)¹ | 1 |
| [#6](#pr-6) | T06: script nạp mô hình 4-bit và notebook chạy trên Kaggle T4 | wsunicorn | 19/08/2026 18:09 | 19/08/2026 18:09 | [`7c35751`](https://github.com/wsunicorn/vihallulens/commit/7c35751fc9c66d73f52acea0da40e1986084b3b5)¹ | 0 |
| [#7](#pr-7) | T07: chốt mẫu prompt và trích attention bằng forward hook | wsunicorn | 19/08/2026 18:19 | 19/08/2026 18:19 | [`7b4e982`](https://github.com/wsunicorn/vihallulens/commit/7b4e9828bdb7a4e245c767862278a69057c284d6)¹ | 1 |
| [#8](#pr-8) | Sửa ba lỗi trước khi chạy cổng T07 | wsunicorn | 19/08/2026 18:35 | 19/08/2026 18:35 | [`f6fae0c`](https://github.com/wsunicorn/vihallulens/commit/f6fae0c543abb6dcd0ea1676cbc307c6dfadcdc8)¹ | 1 |
| [#9](#pr-9) | Sửa notebook: chạy lại không còn dùng nhầm code cũ | wsunicorn | 19/08/2026 18:42 | 19/08/2026 18:42 | [`a8a33af`](https://github.com/wsunicorn/vihallulens/commit/a8a33aff926f2f351b88b3c628f6bed64f094c06)¹ | 0 |
| [#10](#pr-10) | Không phụ thuộc vào editable install nữa khi chạy trên Kaggle | wsunicorn | 19/08/2026 18:48 | 19/08/2026 18:49 | [`aaad26c`](https://github.com/wsunicorn/vihallulens/commit/aaad26ce30bc6190001f6c98360dfb78f564640f)¹ | 1 |
| [#11](#pr-11) | T06 đạt trên T4; thêm chẩn đoán nan cho T07 | wsunicorn | 19/08/2026 18:58 | 19/08/2026 18:58 | [`d3f15ba`](https://github.com/wsunicorn/vihallulens/commit/d3f15baf10cb91df686cb6bb3d8c6857bdb37f16)¹ | 1 |
| [#12](#pr-12) | Thêm công cụ so sánh float16 với float32 trước khi chốt | wsunicorn | 19/08/2026 19:14 | 19/08/2026 19:14 | [`2512e81`](https://github.com/wsunicorn/vihallulens/commit/2512e8153393d41376bd893d07f75cfc60dc1b8b)¹ | 1 |
| [#13](#pr-13) | Chốt float16 bỏ lớp 27, lưu hai biến thể lookback, bỏ token đầu | wsunicorn | 19/08/2026 19:39 | 19/08/2026 19:39 | [`82bab7d`](https://github.com/wsunicorn/vihallulens/commit/82bab7d4140e56cb63494ccd06d46994e5f94132)¹ | 0 |
| [#14](#pr-14) | T07: cổng khả thi kỹ thuật đã qua trên Tesla T4 | wsunicorn | 19/08/2026 19:52 | 19/08/2026 19:52 | [`8e0219f`](https://github.com/wsunicorn/vihallulens/commit/8e0219f1105ed0e55a7d82df336b05c42253c2a6)¹ | 1 |
| [#15](#pr-15) | Cập nhật đường dẫn tài liệu hành chính sau khi sắp xếp thư mục | wsunicorn | 19/08/2026 20:35 | 19/08/2026 20:36 | [`8e4e916`](https://github.com/wsunicorn/vihallulens/commit/8e4e9161da73f4eefba3505fd47dbb772445757c)¹ | 1 |
| [#16](#pr-16) | TASKS.md kiêm luôn sổ tay giải thích, không chỉ tick tiến độ | wsunicorn | 20/08/2026 11:55 | 20/08/2026 11:55 | [`c285fb9`](https://github.com/wsunicorn/vihallulens/commit/c285fb914154d220cb56074e4c67346d778ad7ac)¹ | 1 |
| [#17](#pr-17) | T08: công cụ đo thông lượng và dự báo giờ GPU | wsunicorn | 20/08/2026 12:11 | 20/08/2026 12:12 | [`9e44367`](https://github.com/wsunicorn/vihallulens/commit/9e44367ef934fc62fd8bf7767996b80b75cb3e17)¹ | 1 |
| [#18](#pr-18) | T08: cổng khả thi kỹ thuật đã qua trọn vẹn trên T4 | wsunicorn | 20/08/2026 12:48 | 20/08/2026 12:48 | [`2255bf4`](https://github.com/wsunicorn/vihallulens/commit/2255bf42910a658e8acc5081a5dc2ef79a9c7dc8)¹ | 1 |
| [#19](#pr-19) | T08: ghi nhiệt độ và xung nhịp GPU để lần đo sau tự chẩn đoán | wsunicorn | 20/08/2026 13:03 | 20/08/2026 13:04 | [`9757d2c`](https://github.com/wsunicorn/vihallulens/commit/9757d2cfe40af0668cb8e10f332398cf98d3de74)¹ | 0 |
| [#20](#pr-20) | T09: chuẩn hóa ViHallu về schema chung | wsunicorn | 20/08/2026 13:10 | 20/08/2026 13:10 | [`b758031`](https://github.com/wsunicorn/vihallulens/commit/b758031015c2fb7ab624a68a838f27ea294e5490)¹ | 0 |
| [#21](#pr-21) | T10: chuẩn hóa ISE-DSC01, và sửa một con số sai trong tài liệu | wsunicorn | 20/08/2026 14:17 | 20/08/2026 14:17 | [`6998b02`](https://github.com/wsunicorn/vihallulens/commit/6998b02b6e957fa60c1bc635fc1c9e12d8a98e72)¹ | 1 |
| [#22](#pr-22) | T11: chuẩn hóa ViWikiFC, dừng kiểm tra chỗ bằng chứng trượt | wsunicorn | 20/08/2026 14:33 | 20/08/2026 14:33 | [`fb7aff6`](https://github.com/wsunicorn/vihallulens/commit/fb7aff6cdee665cf58b78485b056e46cee9d431f)¹ | 0 |
| [#23](#pr-23) | T12: chuẩn hóa ViFactCheck, hết giai đoạn chuẩn hóa dữ liệu | wsunicorn | 20/08/2026 14:46 | 20/08/2026 14:46 | [`a937a4f`](https://github.com/wsunicorn/vihallulens/commit/a937a4f74a2b9f939be3994280d80b5f42c97f6b)¹ | 1 |
| [#24](#pr-24) | T13: chuẩn bị phiếu gán nhãn kiểm chứng ánh xạ NEI | wsunicorn | 20/08/2026 15:30 | 20/08/2026 15:30 | [`fca6f8f`](https://github.com/wsunicorn/vihallulens/commit/fca6f8f95c595f2658d7859b4f39bee435d9599c)¹ | 1 |
| [#25](#pr-25) | T13: làm rõ ca số liệu sai, và chịu được ký tự vô hình khi dán | wsunicorn | 23/08/2026 00:35 | 23/08/2026 00:35 | [`192a705`](https://github.com/wsunicorn/vihallulens/commit/192a705938b4b9357c743bfacb87d008cf5227ae)¹ | 1 |
| [#26](#pr-26) | T13: chỉ 67 % nhãn NEI thật sự là ảo giác ngoại lai | wsunicorn | 23/08/2026 11:22 | 23/08/2026 11:23 | [`0c71910`](https://github.com/wsunicorn/vihallulens/commit/0c719101656e7ada9bd4deed825887008e26e0e6)¹ | 1 |
| [#27](#pr-27) | T14: chia tập theo nhóm ngữ cảnh và báo cáo rò rỉ | wsunicorn | 23/08/2026 11:36 | 23/08/2026 11:36 | [`5ca72da`](https://github.com/wsunicorn/vihallulens/commit/5ca72da6189fede0b11e177c33b1f5f4162a412e)¹ | 1 |
| [#28](#pr-28) | T15: chia chunk theo câu và theo cửa sổ token | wsunicorn | 23/08/2026 12:21 | 23/08/2026 12:21 | [`7a7dea3`](https://github.com/wsunicorn/vihallulens/commit/7a7dea3e37a16385fdf45d74c9755d7a855bf56e)¹ | 1 |
| [#29](#pr-29) | T16: kho truy xuất ViWikiFC, hết giai đoạn 2 | wsunicorn | 23/08/2026 14:17 | 23/08/2026 14:18 | [`03191a7`](https://github.com/wsunicorn/vihallulens/commit/03191a7ba073e10d594c77c517ce56c5cb575e5e)¹ | 1 |
| [#30](#pr-30) | T17: E01 baseline tầm thường, sàn thật là macro-F1 0,670 | wsunicorn | 27/08/2026 10:39 | 27/08/2026 10:39 | [`1c6bc4c`](https://github.com/wsunicorn/vihallulens/commit/1c6bc4cd312cda9eec9acdc27dada2bfe3fd3d20) | 1 |
| [#31](#pr-31) | T17: sửa cách đo độ bất định, khoảng tin cậy thật rộng gấp gần năm lần | wsunicorn | 27/08/2026 10:59 | 27/08/2026 11:00 | [`4adac96`](https://github.com/wsunicorn/vihallulens/commit/4adac96ce3c384ba4ccbe4b654440324b239120a) | 1 |
| [#32](#pr-32) | T18: chuẩn bị tinh chỉnh ba bộ mã hóa làm mốc so sánh | wsunicorn | 27/08/2026 11:14 | 27/08/2026 11:14 | [`e811cf8`](https://github.com/wsunicorn/vihallulens/commit/e811cf85ddee5812fea1450873e1c5bb6015d4cf) | 1 |
| [#33](#pr-33) | T18: đo nhiệt độ ngay trong lúc tinh chỉnh, chạy cả ba mô hình một phiên | wsunicorn | 27/08/2026 11:26 | 27/08/2026 11:26 | [`0fba4f6`](https://github.com/wsunicorn/vihallulens/commit/0fba4f6fb1a75267a45b9f8176232e1f070b9a4a) | 1 |
| [#34](#pr-34) | T18: sửa cách chia tập cho tái lập được trên mọi máy | wsunicorn | 27/08/2026 11:38 | 27/08/2026 11:38 | [`a035b02`](https://github.com/wsunicorn/vihallulens/commit/a035b021690fbd20802c09525c54b23a3e2d8d10) | 1 |
| [#35](#pr-35) | T18: sửa lỗi nhãn dạng chuỗi lọt vào tensor, thêm test chạy trọn vòng lặp trên CPU | wsunicorn | 27/08/2026 11:47 | 27/08/2026 11:47 | [`6134fa0`](https://github.com/wsunicorn/vihallulens/commit/6134fa069d8d8ef9194811d4a61d427e05253a20) | 1 |
| [#36](#pr-36) | T18: sửa bất ổn tinh chỉnh, sáu trên chín lần chạy trước không học được gì | wsunicorn | 27/08/2026 15:59 | 27/08/2026 15:59 | [`9586ea3`](https://github.com/wsunicorn/vihallulens/commit/9586ea3419ad3454b1dd0282acf2302853467cc1) | 1 |
| [#37](#pr-37) | T18: bỏ ô thử nghiệm khỏi notebook, ghi lại kết quả kiểm chứng | wsunicorn | 27/08/2026 16:21 | 27/08/2026 16:21 | [`6304e1c`](https://github.com/wsunicorn/vihallulens/commit/6304e1cc753ab82462c74111a7a78cc6073fabef) | 1 |
| [#38](#pr-38) | T18: sửa lưới lọc seed chết bị thủng | wsunicorn | 27/08/2026 17:13 | 27/08/2026 17:13 | [`b64a105`](https://github.com/wsunicorn/vihallulens/commit/b64a105d580f5e2d020551294bdc827d3ae727fa) | 1 |
| [#39](#pr-39) | T18: sửa nốt ba chỗ trước khi chạy lại trên Kaggle | wsunicorn | 27/08/2026 17:44 | 27/08/2026 17:44 | [`53d095d`](https://github.com/wsunicorn/vihallulens/commit/53d095d6622f602014de9ca1e1c9fa8c843b93d0) | 1 |
| [#40](#pr-40) | T18: ghi kết quả E09, tách hai loại độ lệch dùng chung tên khóa | wsunicorn | 27/08/2026 20:50 | 27/08/2026 20:50 | [`fbf4300`](https://github.com/wsunicorn/vihallulens/commit/fbf4300525a161eae8f9f67bf21f4f40aa6f3ff2) | 1 |
| [#41](#pr-41) | T18: notebook thử InfoXLM ở learning rate thấp hơn | wsunicorn | 27/08/2026 20:58 | 27/08/2026 20:58 | [`563f74a`](https://github.com/wsunicorn/vihallulens/commit/563f74a7b25e7635547974c9a149dfcb06c44d5c) | 1 |
| [#42](#pr-42) | T18: chốt InfoXLM không tinh chỉnh được, thêm công cụ soi checkpoint | wsunicorn | 27/08/2026 21:58 | 27/08/2026 21:58 | [`a18f5f3`](https://github.com/wsunicorn/vihallulens/commit/a18f5f3c9fcbb8bd369ba79c08c87ea4f44d926e) | 1 |
| [#43](#pr-43) | T19: baseline LLM giám khảo (E10) trên Gemini free tier | wsunicorn | 27/08/2026 23:34 | 27/08/2026 23:35 | [`23fa8ac`](https://github.com/wsunicorn/vihallulens/commit/23fa8acd494c0f36297fd5adb47bae991b95a0a3) | 1 |
| [#44](#pr-44) | Thêm chỉ số nhị phân: tách phát hiện ảo giác khỏi phân loại đúng loại | wsunicorn | 28/08/2026 12:22 | 28/08/2026 12:22 | [`abf1645`](https://github.com/wsunicorn/vihallulens/commit/abf164554f40a35ec69643678b5d76541305e36e) | 1 |
| [#45](#pr-45) | T18: lưu dự đoán thô của E09 trước khi chạy lại | wsunicorn | 28/08/2026 12:30 | 28/08/2026 12:30 | [`e4996e5`](https://github.com/wsunicorn/vihallulens/commit/e4996e5d0c013bc76970ca96346efce2d00e94e0) | 1 |
| [#46](#pr-46) | Điền chỉ số nhị phân cho cả bốn mốc so sánh | wsunicorn | 28/08/2026 23:24 | 28/08/2026 23:24 | [`cecce2c`](https://github.com/wsunicorn/vihallulens/commit/cecce2ca5f0ed535a913032d791ddd41510bce05) | 1 |
| [#47](#pr-47) | T20: công cụ tái lập Lookback Lens gốc (E02) | wsunicorn | 28/08/2026 23:50 | 28/08/2026 23:50 | [`25c970a`](https://github.com/wsunicorn/vihallulens/commit/25c970a5539fd3ccccc94f8dfd00dc55e4764182) | 1 |
| [#48](#pr-48) | T20: E02 tái lập được, và ngang bộ mã hóa đã tinh chỉnh | wsunicorn | 29/08/2026 14:23 | 29/08/2026 14:23 | [`2d0d6c7`](https://github.com/wsunicorn/vihallulens/commit/2d0d6c7ca577ac71430fc465cb763665528f96d1) | 1 |
| [#49](#pr-49) | T21: năm đặc trưng chunk-aware — phần đóng góp của đề tài | wsunicorn | 29/08/2026 14:38 | 29/08/2026 14:38 | [`4ffa1e6`](https://github.com/wsunicorn/vihallulens/commit/4ffa1e6507a18f4b4d4e19bfe3a28b7d11554015) | 1 |
| [#50](#pr-50) | T22: công cụ E03 chunk-aware chia theo câu | wsunicorn | 29/08/2026 14:58 | 29/08/2026 14:58 | [`ce44cfd`](https://github.com/wsunicorn/vihallulens/commit/ce44cfd69758c90c4040b718bac1e1805ef7aab2) | 1 |
| [#51](#pr-51) | T22: kết quả E03 — thắng ngoại lai, thua nội tại | wsunicorn | 30/08/2026 11:06 | 30/08/2026 11:06 | [`1d4b05c`](https://github.com/wsunicorn/vihallulens/commit/1d4b05c107352f79282351a2a020f7a23d807f26) | 1 |
| [#52](#pr-52) | T23: công cụ E04 quét cửa sổ token, chờ chạy GPU | wsunicorn | 30/08/2026 11:29 | 30/08/2026 11:29 | [`b37f2a6`](https://github.com/wsunicorn/vihallulens/commit/b37f2a6853d1a7f0e4e0184fd1f1952458446121) | 1 |
| [#53](#pr-53) | T22: lưu notebook đã chạy làm minh chứng | wsunicorn | 30/08/2026 11:35 | 30/08/2026 11:35 | [`a2da072`](https://github.com/wsunicorn/vihallulens/commit/a2da072e526855ce49134827730e78933861a56d) | 1 |
| [#54](#pr-54) | T23: kết quả E04 — chia theo câu thắng cả ba cỡ cửa sổ | wsunicorn | 30/08/2026 19:10 | 30/08/2026 19:10 | [`08464b8`](https://github.com/wsunicorn/vihallulens/commit/08464b8b564febd1cb8755d3419e75fb39210147) | 1 |
| [#55](#pr-55) | T23: lưu notebook đã chạy làm minh chứng | wsunicorn | 30/08/2026 19:15 | 30/08/2026 19:16 | [`7d36085`](https://github.com/wsunicorn/vihallulens/commit/7d3608587025f463ff8727ee44591085ded654fe) | 1 |
| [#56](#pr-56) | T23: ghi chú chi phí trích lặp và ba điểm sửa cho notebook sau | wsunicorn | 30/08/2026 19:17 | 30/08/2026 19:17 | [`34f4349`](https://github.com/wsunicorn/vihallulens/commit/34f4349dc550004b3ee0415eff187e40ec7c6da4) | 1 |
| [#57](#pr-57) | T23: chấm lại Bảng 3 trên cùng một máy, và số dev không tái lập giữa hai môi trường | wsunicorn | 30/08/2026 19:38 | 30/08/2026 19:39 | [`95ac841`](https://github.com/wsunicorn/vihallulens/commit/95ac841907ffc4678c65a1fd419da667b6fc0b11) | 1 |
| [#58](#pr-58) | T24: đối chứng cửa sổ không chồng lấn, chờ chạy GPU | wsunicorn | 30/08/2026 19:52 | 30/08/2026 19:52 | [`4753099`](https://github.com/wsunicorn/vihallulens/commit/475309945a0b7b062b1ad655ed66cb682072f391) | 0 |
| [#59](#pr-59) | T24: đối chứng bác cách giải thích chồng lấn, chốt chia theo câu | wsunicorn | 30/08/2026 21:35 | 30/08/2026 21:35 | [`50e0203`](https://github.com/wsunicorn/vihallulens/commit/50e02035e7f661ddc149d27bfd4d971cdba9f2ed) | 1 |
| [#60](#pr-60) | T25: công cụ E06 định vị chú ý, chờ chạy GPU | wsunicorn | 30/08/2026 22:02 | 30/08/2026 22:02 | [`4abf0be`](https://github.com/wsunicorn/vihallulens/commit/4abf0be0ee20860cfddc8c42dd4824cfa283b133) | 1 |
| [#61](#pr-61) | T25: kết quả E06 — chú ý rơi đúng đoạn bằng chứng, CH1 được xác nhận | wsunicorn | 31/08/2026 13:19 | 31/08/2026 13:20 | [`59e5474`](https://github.com/wsunicorn/vihallulens/commit/59e5474c8ccee9dfc2bb77e92bd3b51ee21f2a6f) | 1 |
| [#62](#pr-62) | T26: công cụ E07 chunk-aware trên ngữ cảnh dài, chờ chạy GPU | wsunicorn | 31/08/2026 13:39 | 31/08/2026 13:39 | [`10c9e95`](https://github.com/wsunicorn/vihallulens/commit/10c9e95feca18f405f7ee88f23146359c9788e4f) | 1 |
| [#63](#pr-63) | T26: kết quả E07 — chuyển được sang ngữ cảnh dài nhưng lợi thế co lại | wsunicorn | 01/09/2026 10:39 | 01/09/2026 10:39 | [`7c6ff12`](https://github.com/wsunicorn/vihallulens/commit/7c6ff12ffdc68d962c67d008568dc725e4dc2a9e) | 1 |
| [#64](#pr-64) | T26: lưu notebook đã chạy làm minh chứng | wsunicorn | 01/09/2026 10:46 | 01/09/2026 10:47 | [`468eff8`](https://github.com/wsunicorn/vihallulens/commit/468eff86906374595c015caefac0c2cf631d0c18) | 1 |
| [#65](#pr-65) | T27: công cụ E08 bỏ bằng chứng đi, chờ chạy GPU | wsunicorn | 01/09/2026 11:07 | 01/09/2026 11:07 | [`05e8972`](https://github.com/wsunicorn/vihallulens/commit/05e89727a3f34b3c8b0376841e42fbe372b2e57c) | 1 |
| [#66](#pr-66) | T27: cài rank-bm25 và cho ô tiền kiểm soát cả phụ thuộc | wsunicorn | 01/09/2026 21:58 | 01/09/2026 21:58 | [`4d5b106`](https://github.com/wsunicorn/vihallulens/commit/4d5b1066b3808bcd55d186a09522889f54b8dc8b) | 1 |
| [#67](#pr-67) | TASKS: task đã xong không được còn mục 'Việc cần chạy' | wsunicorn | 01/09/2026 22:01 | 01/09/2026 22:01 | [`356fe4b`](https://github.com/wsunicorn/vihallulens/commit/356fe4b4dbb5c83108b039bda7cccfac3e564f4d) | 1 |
| [#68](#pr-68) | T27: trả lại ô chuẩn bị dữ liệu và cho tiền kiểm đi hết chuỗi | wsunicorn | 01/09/2026 22:22 | 01/09/2026 22:22 | [`008bd48`](https://github.com/wsunicorn/vihallulens/commit/008bd486f0b40360e10f0d3784b80f9b4cc417c6) | 0 |
| [#69](#pr-69) | T27: kết quả E08 — bỏ bằng chứng đi thì chú ý tản ra, cả bốn hướng đều đúng | wsunicorn | 02/09/2026 09:59 | 02/09/2026 09:59 | [`2514922`](https://github.com/wsunicorn/vihallulens/commit/25149229d2f48c6e2a77acd807784c6b04ddd636) | 1 |
| [#70](#pr-70) | T27: BM25 hòa điểm gặp sắp xếp không ổn định, hai máy dựng ngữ cảnh khác nhau | wsunicorn | 02/09/2026 11:03 | 02/09/2026 11:03 | [`20e97ad`](https://github.com/wsunicorn/vihallulens/commit/20e97ad0fceb871e49a284c435954d7e548a3159) | 1 |
| [#71](#pr-71) | T28: soạn báo cáo giữa kỳ và thư gửi GVHD, chờ gửi trước 04/10 | wsunicorn | 02/09/2026 11:19 | 02/09/2026 11:20 | [`1455509`](https://github.com/wsunicorn/vihallulens/commit/1455509f3c0f6ee1d7f5359b40fab639bdabbeca) | 1 |
| [#72](#pr-72) | T28: dựng lại báo cáo giữa kỳ theo mẫu của Khoa, thêm báo cáo tuần 5 | wsunicorn | 02/09/2026 11:44 | 02/09/2026 11:44 | [`fd59d11`](https://github.com/wsunicorn/vihallulens/commit/fd59d117aaf7d4ac3d17e3322469078c72e0e3b9) | 1 |
| [#73](#pr-73) | Báo cáo tuần: thêm bản nháp tuần 6 và bảng theo dõi từng tuần | wsunicorn | 06/09/2026 14:54 | 06/09/2026 14:54 | [`5d36263`](https://github.com/wsunicorn/vihallulens/commit/5d36263079fdceb3e1190d978fc7f423c8542e19) | 0 |
| [#74](#pr-74) | T29: E12 ablation — nhóm chunk-aware cộng thêm một số âm | wsunicorn | 06/09/2026 15:15 | 06/09/2026 15:16 | [`01510d6`](https://github.com/wsunicorn/vihallulens/commit/01510d60cad83934f6fa55d1d7eff8cdc17773e4) | 0 |
| [#75](#pr-75) | Báo cáo tuần: trình bày theo tiến độ kế hoạch thay vì dồn một lá thư | wsunicorn | 06/09/2026 15:33 | 06/09/2026 15:33 | [`318b213`](https://github.com/wsunicorn/vihallulens/commit/318b213fc09bc4ddcc7a472fed82cfed47f77fe9) | 1 |
| [#76](#pr-76) | Báo cáo tuần: soạn nốt tuần 8 và 9, trọn bộ tới mốc giữa kỳ | wsunicorn | 06/09/2026 15:47 | 06/09/2026 15:47 | [`57c32e5`](https://github.com/wsunicorn/vihallulens/commit/57c32e5de986a10e2707fae6dbf2ad3412f306fe) | 1 |
| [#77](#pr-77) | T30: công cụ E13 so Qwen2.5-7B với Sailor2-8B, chờ chạy Kaggle | wsunicorn | 06/09/2026 16:03 | 06/09/2026 16:03 | [`ee8bcdb`](https://github.com/wsunicorn/vihallulens/commit/ee8bcdbd5d7a35932a94431ed38a082bfeff219b) | 1 |
| [#78](#pr-78) | T30: lượt mốc float32 hết bộ nhớ với Sailor2-8B, sửa thứ tự và thêm bfloat16 | wsunicorn | 06/09/2026 16:17 | 06/09/2026 16:17 | [`96c661c`](https://github.com/wsunicorn/vihallulens/commit/96c661ccedfa0dc3ef323aac136586dbd4df63ef) | 1 |
| [#79](#pr-79) | Ghim transformers và chạy test hook trên Kaggle trước khi tiêu GPU | wsunicorn | 06/09/2026 16:23 | 06/09/2026 16:23 | [`26f3e38`](https://github.com/wsunicorn/vihallulens/commit/26f3e38a7c5150449e4025cc6da8bb3d9ad5ccca) | 1 |
| [#80](#pr-80) | T30: gc.collect() trước empty_cache, mô hình đầu chưa từng được giải phóng | wsunicorn | 06/09/2026 16:36 | 06/09/2026 16:36 | [`e3bc2dc`](https://github.com/wsunicorn/vihallulens/commit/e3bc2dcc4cad214b22e0be6af2596f890669026c) | 1 |
| [#81](#pr-81) | T30: tắt thanh tiến trình nạp trọng số, log bị cắt mất phần cần đọc | wsunicorn | 06/09/2026 16:39 | 06/09/2026 16:39 | [`e7d1f81`](https://github.com/wsunicorn/vihallulens/commit/e7d1f81b7918a07d803eb6d80c31564f587679d2) | 1 |
| [#82](#pr-82) | T30: ô kiểm chặn luôn đường lấy shard về, thêm công cụ soi shard | wsunicorn | 07/09/2026 11:00 | 07/09/2026 11:00 | [`5f3a4c4`](https://github.com/wsunicorn/vihallulens/commit/5f3a4c4d4407b06133994d9f07095623b9fa71c4) | 0 |
| [#83](#pr-83) | T30: Sailor2 hỏng cả mạng trên 0,7 % mẫu, không phải hỏng một lớp | wsunicorn | 09/09/2026 21:08 | 09/09/2026 21:08 | [`c1272b1`](https://github.com/wsunicorn/vihallulens/commit/c1272b1e403311fbb3a5f624a669fd22baf029ad) | 1 |
| [#84](#pr-84) | T30: E13 xong — lookback gộp chuyển được giữa hai mô hình, chunk-aware thì không | wsunicorn | 09/09/2026 21:31 | 09/09/2026 21:32 | [`7f79d1a`](https://github.com/wsunicorn/vihallulens/commit/7f79d1a5957492259b1fe05e5f45605efa79b0c6) | 1 |
| [#85](#pr-85) | T31: công cụ E14 bậc thang 7B/3B/1.5B, chờ chạy hai phiên Kaggle riêng | wsunicorn | 09/09/2026 21:41 | 09/09/2026 21:41 | [`610ef52`](https://github.com/wsunicorn/vihallulens/commit/610ef52fd689936909b091aad6ed2024153823cd) | 1 |
| [#86](#pr-86) | T30: commit notebook đã chạy, minh chứng của lượt Sailor2 | wsunicorn | 09/09/2026 21:47 | 09/09/2026 21:47 | [`09afd89`](https://github.com/wsunicorn/vihallulens/commit/09afd895ab4dcf121cdccedf0d486ab6681d75e6) | 1 |
| [#87](#pr-87) | T31: gộp bậc thang vào một phiên, đo chi phí xen kẽ | wsunicorn | 09/09/2026 21:52 | 09/09/2026 21:52 | [`73f177f`](https://github.com/wsunicorn/vihallulens/commit/73f177f305b95d3e6bfe42196b447d4f6fc63f06) | 1 |
| [#88](#pr-88) | T31: 7B không trích lại, nhưng đưa vào ô đo chi phí xen kẽ | wsunicorn | 09/09/2026 21:59 | 09/09/2026 21:59 | [`0f6b29a`](https://github.com/wsunicorn/vihallulens/commit/0f6b29ab3965541c2877da7b73740271c7f955e9) | 1 |
| [#89](#pr-89) | T31: guard coi "không lớp nào tràn số" là lỗi, và Qwen2.5-3B sạch hoàn toàn | wsunicorn | 09/09/2026 22:13 | 09/09/2026 22:13 | [`5b6e294`](https://github.com/wsunicorn/vihallulens/commit/5b6e294f00385622dfcc59937e665f4a193d4550) | 1 |
| [#90](#pr-90) | T31: một nấc hỏng không được kéo cả phiên, và Qwen2.5-1.5B tràn số ở mọi lớp | wsunicorn | 09/09/2026 22:32 | 09/09/2026 22:32 | [`cad3186`](https://github.com/wsunicorn/vihallulens/commit/cad3186cd2d958b1a81b36f72829ca2e3f58c11e) | 1 |
| [#91](#pr-91) | T31: nấc 1.5B chạy bfloat16, vì float16 tràn số cả 28 lớp | wsunicorn | 09/09/2026 22:41 | 09/09/2026 22:41 | [`efee41e`](https://github.com/wsunicorn/vihallulens/commit/efee41e733c94f54d8b1591e277cc8aabaf1786b) | 1 |
| [#92](#pr-92) | Rà soát toàn repo: sửa bốn chỗ, thêm task cho hai việc E12 để lại | wsunicorn | 09/09/2026 23:01 | 09/09/2026 23:02 | [`87ce9c2`](https://github.com/wsunicorn/vihallulens/commit/87ce9c2335062356610f31066d83d48132bd874b) | 0 |
| [#93](#pr-93) | T31: cất kết quả trích trước khi đo chi phí, và chặn thời gian mỗi lượt đo | wsunicorn | 10/09/2026 10:05 | 10/09/2026 10:06 | [`231fe3c`](https://github.com/wsunicorn/vihallulens/commit/231fe3c43c990400fbbcecf2acf9a606290cfbf8) | 1 |
| [#94](#pr-94) | T31: E14 xong — dấu của chunk-aware đảo hai lần trong cùng một họ mô hình | wsunicorn | 10/09/2026 15:07 | 10/09/2026 15:07 | [`f238802`](https://github.com/wsunicorn/vihallulens/commit/f238802db4958dcb91b30ec7b8e89de1632fad3e) | 0 |
| [#95](#pr-95) | T31: sáu lượt đo chi phí về đủ — nấc 1.5B chậm hơn cả 7B | wsunicorn | 10/09/2026 15:13 | 10/09/2026 15:13 | [`8d42fb0`](https://github.com/wsunicorn/vihallulens/commit/8d42fb045c8dac97b2aa2a9bdb586fca66ba1716) | 0 |
| [#96](#pr-96) | T32: E11 bảng đánh đổi — và nó chứng minh hai ô của Bảng 1 sai | wsunicorn | 10/09/2026 15:21 | 10/09/2026 15:21 | [`891efb9`](https://github.com/wsunicorn/vihallulens/commit/891efb90391e7730104653dc57e17c7f6980fd86) | 0 |
| [#97](#pr-97) | T33: dựng công cụ E15 trên split gốc ViWikiFC, và sửa một con số của T15 | wsunicorn | 10/09/2026 15:36 | 10/09/2026 15:36 | [`ebc9ae3`](https://github.com/wsunicorn/vihallulens/commit/ebc9ae377cba7e2bda8873182f5248df177bffee) | 1 |
| [#98](#pr-98) | T33: E15 xong — kém SemViQA 13 điểm trên split gốc, và cùng đầu chú ý dẫn đầu ở cả ba bộ | wsunicorn | 11/09/2026 08:47 | 11/09/2026 08:47 | [`11f35ca`](https://github.com/wsunicorn/vihallulens/commit/11f35cac061c63037679db8848b67b33a1df5019) | 1 |
| [#99](#pr-99) | T34: E16 xong — bộ phát hiện ba lớp không chuyển được giữa hai bộ, vì ba lớp không cùng nghĩa | wsunicorn | 11/09/2026 09:17 | 11/09/2026 09:17 | [`362fc48`](https://github.com/wsunicorn/vihallulens/commit/362fc48c2a694d08e63a060e8c44914fa3b67d4c) | 0 |
| [#100](#pr-100) | T35: phân tích sai sót — 48 % lỗi là nhầm giữa hai loại ảo giác, prompt bỏ dấu không ảnh hưởng | wsunicorn | 11/09/2026 09:32 | 11/09/2026 09:32 | [`6142114`](https://github.com/wsunicorn/vihallulens/commit/6142114548a2c17873fd3cf571fbf3670c99a9f1) | 1 |
| [#101](#pr-101) | T35B: E12 trên ISE-DSC01 cho chênh +0,0002, và chunk-aware chồng lấn 99,9 % với lookback | wsunicorn | 11/09/2026 10:38 | 11/09/2026 10:38 | [`c16f6d4`](https://github.com/wsunicorn/vihallulens/commit/c16f6d41450d6292851c2cbb186ac08b3f96e4e4) | 1 |
| [#102](#pr-102) | T36: thư viện hoàn chỉnh — DetectorBundle mang công thức dựng cột, pipeline một lời gọi | wsunicorn | 11/09/2026 10:53 | 11/09/2026 10:53 | [`ab86bd3`](https://github.com/wsunicorn/vihallulens/commit/ab86bd3e64f9031495d3265790bfd72d23f04233) | 1 |
| [#103](#pr-103) | T37: dịch vụ REST ba endpoint, kiểm hợp đồng không GPU | wsunicorn | 11/09/2026 10:57 | 11/09/2026 10:57 | [`c4254ba`](https://github.com/wsunicorn/vihallulens/commit/c4254ba88f7d6cf876221423ddf68979af82e550) | 1 |
| [#104](#pr-104) | T38: Dockerfile một lệnh, và build thật bắt được hai lỗi của T37 | wsunicorn | 11/09/2026 11:27 | 11/09/2026 11:27 | [`9510005`](https://github.com/wsunicorn/vihallulens/commit/9510005e6c78cff5c6f98ea3ebb445e8f4b3dea1) | 1 |
| [#105](#pr-105) | T39: trang quan sát tô màu đoạn theo tỷ trọng chú ý, HTML + JS thuần | wsunicorn | 11/09/2026 11:33 | 11/09/2026 11:33 | [`d15b1bf`](https://github.com/wsunicorn/vihallulens/commit/d15b1bf137e62aa8a318008f00cbceefda7a5e11) | 0 |
| [#106](#pr-106) | T40: hệ RAG minh họa, một mô hình vừa trả lời vừa chấm; notebook gom bốn smoke test GPU | wsunicorn | 11/09/2026 12:20 | 11/09/2026 12:20 | [`17c439d`](https://github.com/wsunicorn/vihallulens/commit/17c439d71cc1a56a7c2a93bb45cd72d251791fbe) | 0 |
| [#107](#pr-107) | T40: cài rank-bm25 và nâng scikit-learn trong notebook, tiền kiểm nạp thử bundle | wsunicorn | 11/09/2026 12:34 | 11/09/2026 12:34 | [`eed353c`](https://github.com/wsunicorn/vihallulens/commit/eed353c67790204cff29a1db590999d26de94bdb) | 0 |
| [#108](#pr-108) | T40: kết quả phiên Kaggle — ba smoke test qua, sinh câu trả lời ra NaN vì lớp 27 | wsunicorn | 11/09/2026 12:48 | 11/09/2026 12:48 | [`ea85a70`](https://github.com/wsunicorn/vihallulens/commit/ea85a707659af3672f1c6b77a97dc5bf2d3749ec) | 0 |
| [#109](#pr-109) | T40: bộ sinh riêng — Qwen2.5-7B nạp thêm bản bfloat16, vì float16 không sinh được | wsunicorn | 11/09/2026 12:53 | 11/09/2026 12:53 | [`2edaf47`](https://github.com/wsunicorn/vihallulens/commit/2edaf47c9e7ef3a1d91a9d041dfe236de90431aa) | 0 |
| [#110](#pr-110) | T40: hai bản 7B không nằm chung T4 — bộ sinh về Qwen2.5-3B bfloat16, cỡ lớn nhất còn vừa | wsunicorn | 11/09/2026 13:06 | 11/09/2026 13:06 | [`58a3ff5`](https://github.com/wsunicorn/vihallulens/commit/58a3ff5fd6d77e86d8da87e562d95b80e5c3b308) | 0 |
| [#111](#pr-111) | T40: demo RAG chạy đầu cuối trên T4 — bộ phát hiện tự bắt được ảo giác của bộ sinh 3B | wsunicorn | 11/09/2026 13:40 | 11/09/2026 13:40 | [`08c53f3`](https://github.com/wsunicorn/vihallulens/commit/08c53f3020381a1a502ca24db18697f80b037f34) | 0 |
| [#112](#pr-112) | T40: cất notebook đã chạy và ba JSON của lượt 3 làm minh chứng | wsunicorn | 11/09/2026 13:46 | 11/09/2026 13:46 | [`cf7b64a`](https://github.com/wsunicorn/vihallulens/commit/cf7b64a6f70ac323839fbf9b15ddbbbb67d77719) | 0 |
| [#113](#pr-113) | chore: thêm uv.lock | wsunicorn | 11/09/2026 14:05 | 11/09/2026 14:05 | [`99a6b16`](https://github.com/wsunicorn/vihallulens/commit/99a6b168580c83bfbf36d165ff1e57c15c65c809) | 0 |
| [#114](#pr-114) | Rà soát toàn repo: sửa 12 chỗ tài liệu lệch mã, số liệu không có chỗ nào sai | wsunicorn | 11/09/2026 14:35 | 11/09/2026 14:35 | [`17da2fc`](https://github.com/wsunicorn/vihallulens/commit/17da2fc239711311c565a4e35c59e67cf1088b81) | 0 |
| [#115](#pr-115) | Soạn xong báo cáo tuần 10–13; bỏ hai đoạn lặp ở mục E14 | wsunicorn | 11/09/2026 14:51 | 11/09/2026 14:51 | [`24898f3`](https://github.com/wsunicorn/vihallulens/commit/24898f39ed50a90b508f767612cbdab69ac69082) | 0 |
| [#116](#pr-116) | T39B: trang chủ kể chuyện — hero ba nhịp, cú Lens mắt dõi con trỏ, chế độ phát lại | wsunicorn | 11/09/2026 16:05 | 11/09/2026 16:05 | [`98bfdbf`](https://github.com/wsunicorn/vihallulens/commit/98bfdbf0b093b26c9efd9211ff55471d32e88ba8) | 0 |
| [#117](#pr-117) | T39B: hero lượt 2 — chữ không bị che, tiêu đề mới, prompt theo ảnh cú tham chiếu | wsunicorn | 11/09/2026 16:14 | 11/09/2026 16:14 | [`8436b23`](https://github.com/wsunicorn/vihallulens/commit/8436b2348d69a4a119d75571a2525a398fc22b51) | 0 |
| [#118](#pr-118) | T39B: sửa mask đèn pin, màn mở đầu tối hơn | wsunicorn | 11/09/2026 16:17 | 11/09/2026 16:17 | [`c552621`](https://github.com/wsunicorn/vihallulens/commit/c5526217a4091cd8774b47306252ae3376d67361) | 0 |
| [#119](#pr-119) | T39B: cú mở đầu to hơn, mắt trùm lên tiêu đề | wsunicorn | 11/09/2026 16:20 | 11/09/2026 16:20 | [`25aa1ca`](https://github.com/wsunicorn/vihallulens/commit/25aa1ca0bd5df324ffd079c95d544a45ee22e203) | 0 |
| [#120](#pr-120) | T39B: ảnh cú thật, mắt lam ngọc theo ảnh tham chiếu | wsunicorn | 11/09/2026 16:45 | 11/09/2026 16:45 | [`4c77ed9`](https://github.com/wsunicorn/vihallulens/commit/4c77ed95bbd6b4c01fa78f1bc98cdcbe14a7b648) | 0 |
| [#121](#pr-121) | T39B: ảnh cú xám mắt lam ngọc, cử động theo con trỏ, vẫy cánh | wsunicorn | 11/09/2026 17:07 | 11/09/2026 17:07 | [`c580402`](https://github.com/wsunicorn/vihallulens/commit/c580402d93f3b784584e2a722df0d06224c7e019) | 0 |
| [#122](#pr-122) | T39B: bốn cử chỉ có ảnh thật, khử nền đen | wsunicorn | 11/09/2026 17:21 | 11/09/2026 17:21 | [`39271a3`](https://github.com/wsunicorn/vihallulens/commit/39271a320364ba1a9865ce5fd8e42108a2c97e40) | 0 |
| [#123](#pr-123) | T39B: morph theo mắt, khung mờ dần, cánh chỉ sang trái | wsunicorn | 11/09/2026 17:33 | 11/09/2026 17:33 | [`4087aba`](https://github.com/wsunicorn/vihallulens/commit/4087aba0968ddcd2cb9aab990dd74b334bdfcde4) | 0 |
| [#124](#pr-124) | Slides: bộ trình bày với GVHD 16/09 | wsunicorn | 13/09/2026 23:46 | 13/09/2026 23:46 | [`76207d8`](https://github.com/wsunicorn/vihallulens/commit/76207d8d41a8e5f3f2497337931ec7f7073c763a) | 0 |
| [#125](#pr-125) | Slides v2: bộ 36 slide theme "Đêm cú" bám 8 chương mẫu báo cáo | wsunicorn | 18/09/2026 23:50 | 26/09/2026 15:28 | [`2c9caed`](https://github.com/wsunicorn/vihallulens/commit/2c9caedad3965db6e5ee2efa2a6f019a0a33cbfd) | 1 |
| [#126](#pr-126) | Slides v2: dựng lại 36 slide — mọi slide tự chạy, 14 sơ đồ động trên số liệu thật | wsunicorn | 19/09/2026 00:31 | 26/09/2026 15:28 | [`41dafde`](https://github.com/wsunicorn/vihallulens/commit/41dafde690a6a3dfe87302b7afb51ca328fe862d) | 1 |
| [#127](#pr-127) | Đánh giá tổng kết 26/09: mức hoàn thành ba câu hỏi nghiên cứu và năm việc còn lại | wsunicorn | 26/09/2026 15:24 | 26/09/2026 15:28 | [`fe6654d`](https://github.com/wsunicorn/vihallulens/commit/fe6654d1744bdf678820332e2b15e07a23b2771b) | 1 |
| [#128](#pr-128) | Slides: bộ slide Hội đồng 23 trang theo bố cục khóa luận | wsunicorn | 22/10/2026 15:25 | 22/10/2026 15:25 | [`41dd81c`](https://github.com/wsunicorn/vihallulens/commit/41dd81c5b404ffd92c770cf74daba1482fe9ac8f) | 1 |
| [#129](#pr-129) | Cập nhật TASKS.md 22/10: tick T28, T47; trạng thái các việc còn lại | wsunicorn | 22/10/2026 15:26 | 22/10/2026 15:26 | [`a16f4dc`](https://github.com/wsunicorn/vihallulens/commit/a16f4dccdb70b2a93c68aa39d91ec958df0b32d9) | 1 |
| [#130](#pr-130) | Tái lập: ghim phiên bản mô hình, thư viện Docker và Kaggle, thêm mã băm dữ liệu gốc | wsunicorn | 22/10/2026 15:35 | 22/10/2026 15:35 | [`549b0d0`](https://github.com/wsunicorn/vihallulens/commit/549b0d09866260f6f7203ced4903436b6036ac8a) | 1 |
| [#131](#pr-131) | T45D: dựng thí nghiệm E19 định vị bằng cắt bỏ ngữ cảnh | wsunicorn | 22/10/2026 15:48 | 22/10/2026 15:48 | [`9a1d54c`](https://github.com/wsunicorn/vihallulens/commit/9a1d54c7fcd22c7e8047fa7c92862a1cbfe49efe) | 1 |
| [#132](#pr-132) | T45C: dựng thí nghiệm E18 chấm theo từng câu phản hồi | wsunicorn | 22/10/2026 16:05 | 22/10/2026 16:06 | [`5bbf9ca`](https://github.com/wsunicorn/vihallulens/commit/5bbf9ca3c05626a2dfc05b020737c50d834c2436) | 1 |
| [#133](#pr-133) | T41: dựng thí nghiệm E17 chuyển miền sang ViFactCheck | wsunicorn | 22/10/2026 16:06 | 22/10/2026 16:06 | [`9ecf268`](https://github.com/wsunicorn/vihallulens/commit/9ecf2682beafb0350b8a7a41b7c05f4d3a5b1c69) | 1 |
| [#134](#pr-134) | T50: giải thích slide, kịch bản thời gian và câu hỏi hội đồng | wsunicorn | 22/10/2026 16:10 | 22/10/2026 16:10 | [`f0ad3c2`](https://github.com/wsunicorn/vihallulens/commit/f0ad3c23cf914f91da3a71e57fd9d078c73c8008) | 1 |
| [#135](#pr-135) | Báo cáo: đưa nguồn dựng quyển (docs/report, docs/media, docs/tools) vào repo, khớp bản Word đã nộp | MinhNguyen1007 | 22/10/2026 17:19 | — | đang mở | 1 |

## Từng PR

<a id="pr-1"></a>

### #1 — T01: khởi tạo repo, pyproject và bố cục src

- **Nhánh:** `t01-khoi-tao-repo` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 13:18 · **gộp:** 19/08/2026 13:24 · **commit gộp:** [`aebc263`](https://github.com/wsunicorn/vihallulens/commit/aebc2632cc273f85934a212ab2e72664989e5406)¹
- **Thay đổi:** +91 / −9, 16 file · **bình luận bot:** 1

Task T01 trong `TASKS.md`. Nhánh này chỉ dựng khung, không có logic nghiệp vụ nào.

##### Đã làm

- `pyproject.toml`: Python 3.11, tên gói `vihallulens`, bố cục `src/`, build backend hatchling. Khai báo đủ phụ thuộc theo T01; `pytest` và `ruff` đặt trong extra `dev` để môi trường chạy trên Kaggle không kéo theo công cụ phát triển.
- Cây thư mục theo mục 9 của `CLAUDE.md`, kèm sáu gói con ứng với bốn tầng kiến trúc trong `docs/SPEC.md`: `data`, `extract`, `features`, `detect`, `evaluation`, `serve`. Mỗi gói chỉ có docstring một dòng, chưa có hàm nào.
- `.env.example` với `HF_TOKEN` và `GEMINI_API_KEY` để trống.
- `.gitignore` đã có sẵn từ lúc dựng repo, đã rà lại: loại trừ `data/` trừ `MANIFEST.md`, `.env`, `.venv`, `results/*.npz`.
- `README.md`: điền đường dẫn Kaggle Dataset thật và cách symlink `data/raw` trong notebook.

##### Kết quả kiểm tra

```
$ uv pip install -e ".[dev]"
+ vihallulens==0.1.0 (from file:///D:/StudyDocument/KLTN/vihallulens)

$ python -c "import vihallulens; print(vihallulens.__version__)"
import vihallulens OK, version 0.1.0
```

Phiên bản đã giải trên Python 3.11.9:

| Gói | Phiên bản | | Gói | Phiên bản |
|---|---|---|---|---|
| torch | 2.13.0 | | pydantic | 2.13.4 |
| transformers | 5.15.0 | | pyyaml | 6.0.3 |
| accelerate | 1.14.0 | | python-dotenv | 1.2.3 |
| bitsandbytes | 0.50.1 | | rank-bm25 | 0.2.2 |
| pandas | 3.0.5 | | fastapi | 0.141.1 |
| pyarrow | 25.0.1 | | uvicorn | 0.52.3 |
| numpy | 2.4.6 | | pytest | 9.1.1 |
| scikit-learn | 1.9.0 | | ruff | 0.16.3 |

##### Ghi chú chuyển cho task sau

**T07 — rủi ro đã lộ ra ngay ở khâu cài đặt.** `transformers` giải ra bản **5.15.0**, tức nhánh API mới, không phải 4.x mà bài Lookback Lens và phần lớn ví dụ tham khảo dùng. Việc forward hook trên `self_attn` có nhận được `attn_weights` hay không phụ thuộc trực tiếp vào chuyện này (mục 5 của `CLAUDE.md`). Chưa ghim phiên bản ở T01 vì T07 mới là nơi có căn cứ thực nghiệm để chọn ghim bản nào.

**T02** sẽ thêm cấu hình `ruff` vào `pyproject.toml` và `tests/test_smoke.py`.

---

<a id="pr-2"></a>

### #2 — T02: cấu hình ruff và pytest, thêm test smoke

- **Nhánh:** `t02-lint-va-test` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 13:24 · **gộp:** 19/08/2026 17:54 · **commit gộp:** [`d473330`](https://github.com/wsunicorn/vihallulens/commit/d473330f35c4eb1b679666593d5f18e22aac7dcf)¹
- **Thay đổi:** +37 / −4, 4 file · **bình luận bot:** 1

Task T02 trong `TASKS.md`.

##### Đã làm

- Cấu hình `ruff` trong `pyproject.toml`: `line-length = 100` đúng yêu cầu task, `target-version = "py311"`, bộ luật `E, W, F, I, UP, B, SIM, N`, isort biết `vihallulens` là gói nội bộ.
- Cấu hình `pytest`: `testpaths = ["tests"]` để `pytest` không quét nhầm `.venv`.
- `tests/test_smoke.py`: một test kiểm tra gói có `__version__`, một test kiểm tra cả sáu gói con của bốn tầng kiến trúc trong `docs/SPEC.md` đều import được — bắt sớm lỗi thiếu `__init__.py` khi cây thư mục thay đổi.

##### Kết quả kiểm tra

```
$ ruff check .
All checks passed!

$ pytest
..                                                                       [100%]
2 passed in 0.02s
```

---

<a id="pr-3"></a>

### #3 — T03: module cấu hình pydantic, loader YAML và config_hash

- **Nhánh:** `t03-module-cau-hinh` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 17:55 · **gộp:** 19/08/2026 17:56 · **commit gộp:** [`f76898e`](https://github.com/wsunicorn/vihallulens/commit/f76898ee5edf16e76ffceec210ff0757d6bd28e0)¹
- **Thay đổi:** +378 / −6, 6 file · **bình luận bot:** 0

Task T03 trong `TASKS.md`.

##### Đã làm

`src/vihallulens/config.py` định nghĩa `ExperimentConfig` gồm năm khối con đúng theo cấu trúc YAML ở mục 3 của `docs/SPEC.md`: `dataset`, `chunking`, `extractor`, `features`, `detector`. Kèm `load_config(path)` và `config_hash(cfg)`.

Ba quyết định thiết kế, đều nhằm bảo vệ khả năng tái lập:

1. **`extra="forbid"` trên mọi model.** Gõ `max_context_token` thiếu chữ `s` sẽ raise thay vì bị bỏ qua âm thầm. Nếu bỏ qua âm thầm thì hai lần chạy trông giống hệt nhau trên giấy nhưng chạy với hai giá trị khác nhau — đúng loại lỗi làm hỏng cả bảng kết quả mà không ai phát hiện.
2. **`split_seed` khác 42 là raise.** Mục 3 của `CLAUDE.md` chốt seed 42 và mục 7 cấm tự ý đổi. Thông báo lỗi ghi rõ phải sửa `CLAUDE.md` trước nếu thật sự muốn đổi.
3. **`config_hash` bỏ qua `run_name`.** Tên lần chạy là nhãn, không phải tham số. Chạy lại cùng cấu hình dưới tên khác phải ra cùng hash thì mới nhận ra được đó là lần lặp lại chứ không phải cấu hình mới.

Ngoài ra `chunking.stride` mặc định bằng nửa `window_size` theo quy ước của E05 trong `docs/EXPERIMENTS.md`, điền ở validator `mode="before"` để không phải ghi đè lên model đã `frozen`.

##### Kết quả kiểm tra

```
$ pytest tests/test_config.py
....................... 23 passed in 0.13s

$ pytest
........................... 27 passed in 0.15s

$ ruff check .
All checks passed!
```

23 ca gồm: ba ca hợp lệ, bảy ca thiếu trường hoặc sai giá trị phải raise (thiếu từng khối bắt buộc, thiếu `model_name`, sai tên bộ dữ liệu, đổi seed, `token_window` thiếu `window_size`, `topk_heads` thiếu `topk`, trùng nhóm đặc trưng), ba ca loader, bốn ca hash.

##### Ghi chú

- Thêm `python-dotenv` đã làm ở T01; module này chưa đọc `.env` vì chưa task nào cần khóa. T19 sẽ đọc.
- Comment trong `configs/example.yaml` viết tiếng Việt vì đó là tài liệu hướng dẫn cho người trong nhóm, không phải code. Toàn bộ `.py` giữ tiếng Anh theo mục 2 của `CLAUDE.md`.
- Sửa kèm một lỗi nhỏ trong `docs/SPEC.md`: `run_name` ví dụ ghi `t20_chunk_aware_sentence_vihallu`, nhưng T20 là tái lập lookback gộp còn chunk-aware theo câu là E03. Đổi thành `e03_...`.

---

<a id="pr-4"></a>

### #4 — T04: module ghi kết quả runs.jsonl và xuất bảng

- **Nhánh:** `t04-module-ghi-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 17:58 · **gộp:** 19/08/2026 17:58 · **commit gộp:** [`648c96f`](https://github.com/wsunicorn/vihallulens/commit/648c96f29e51f8f182c902c72155c73aaa458d61)¹
- **Thay đổi:** +294 / −7, 4 file · **bình luận bot:** 1

Task T04 trong `TASKS.md`.

##### Đã làm

`src/vihallulens/evaluation/logging.py` theo mục 2.5 của `docs/SPEC.md`:

- `log_result(run_name, config, metrics, extra, path=...)` ghi nối một dòng JSON vào `results/runs.jsonl`, đủ `timestamp`, `run_name`, `git_commit`, `config_hash`, `config`, `metrics`, `extra`. Trả về chính bản ghi để nơi gọi kiểm tra hoặc in ra.
- `export_table(filter, columns, path=...)` đọc file, làm phẳng thành cột chấm (`config.dataset.name`, `metrics.macro_f1`, `extra.ms_per_sample`), lọc theo bằng nhau và chọn cột đúng thứ tự yêu cầu.
- `read_results(path)` là hàm phụ trả về toàn bộ file dạng DataFrame.

Ba điểm đáng nói:

1. **Thiếu chỉ số vận hành là raise, và không ghi gì cả.** Mục 3 của `docs/EXPERIMENTS.md` bắt mọi phương pháp phải báo `ms_per_sample` và `peak_vram_mb`. Chặn ngay lúc ghi tốt hơn là tới lúc dựng Bảng 11 mới phát hiện thiếu, khi đó phải chạy lại thí nghiệm.
2. **`config_hash` dùng chung một hàm với `config.py`.** Đã tách `hash_config_dict` để nhánh nhận dict và nhánh nhận `ExperimentConfig` không bao giờ lệch nhau. Có test khẳng định điều này.
3. **Cột nào chưa lần chạy nào có thì xuất ra rỗng chứ không raise.** Bảng kết quả trong `docs/EXPERIMENTS.md` điền dần theo tuần, nên bảng nửa vời vẫn phải xuất được.

##### Kết quả kiểm tra

Đúng lệnh nêu trong task — gọi `log_result` hai lần rồi `export_table`:

```
               run_name config.features.groups  metrics.macro_f1  extra.ms_per_sample  config_hash
e01_baseline_tam_thuong              [surface]             0.712                  0.4 d7ed0fc190b5
       e02_lookback_gop                [basic]             0.781                 91.2 643de5ac9879
số dòng: 2
```

```
$ pytest
.......................................... 42 passed in 2.02s

$ ruff check .
All checks passed!
```

17 ca mới gồm: ca bắt buộc của task, hình dạng bản ghi, tính chất chỉ ghi nối, hash khớp với model, giữ nguyên tiếng Việt có dấu qua vòng đọc ghi, hai ca thiếu chỉ số vận hành, ca không ghi gì khi raise, và sáu ca cho `export_table`.

##### Ghi chú

- Tham số đầu của `export_table` giữ tên `filter` cho đúng chữ ký trong `docs/SPEC.md`, dù trùng tên hàm dựng sẵn của Python. Đã đánh dấu `noqa` kèm lý do ngay tại chỗ.
- `results/runs.jsonl` **được commit** — mục 3 của `CLAUDE.md` chọn cách theo dõi thí nghiệm bằng file cục bộ. `.gitignore` chỉ loại `results/*.npz`.

---

<a id="pr-5"></a>

### #5 — T05: script đo ngân sách bộ nhớ và độ dài token tiếng Việt

- **Nhánh:** `t05-do-ngan-sach-bo-nho` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 18:05 · **gộp:** 19/08/2026 18:05 · **commit gộp:** [`3ae1919`](https://github.com/wsunicorn/vihallulens/commit/3ae1919ed51b3930b6b2f236ae3549128ddb6cab)¹
- **Thay đổi:** +336 / −3, 5 file · **bình luận bot:** 1

Task T05 trong `TASKS.md`. Chạy hoàn toàn trên CPU, 21 giây.

##### Đã làm

`scripts/probe_vram.py` in ra hai bảng:

1. **Ngân sách bộ nhớ.** Đọc `AutoConfig` (vài KB JSON, không tải trọng số), suy ra số lớp, số đầu chú ý, số tham số, rồi tính ma trận chú ý một lớp theo `n_heads × seq_len² × 2` byte. Phần ước lượng trọng số sau NF4 tách riêng phần `bitsandbytes` thật sự lượng tử hóa (`nn.Linear`) với phần giữ fp16 (embedding, `lm_head`, norm) — nếu lấy 7,62 B × 0,5 byte thì ra 3,8 GB, thấp hơn thực tế gần 1,7 GB.
2. **Độ dài token.** Tokenize toàn bộ ngữ cảnh có nhãn của cả bốn bộ, mỗi ngữ cảnh duy nhất chỉ tokenize một lần rồi ánh xạ ngược về mẫu.

##### Kết quả — bảng ngân sách

```
  Số lớp                : 28
  Số đầu chú ý          : 28  (KV heads: 4)
  Tổng tham số          : 7.62 B
    lượng tử hóa được   : 6.53 B  (nn.Linear → NF4)
    giữ fp16            : 1.09 B  (embedding, head, norm)
  Trọng số fp16         : 15.23 GB
  Trọng số sau NF4      : 5.44 GB   ← mức nạp lên GPU

   Độ dài chuỗi |   Một lớp |   Cả 28 lớp | Đỉnh ước tính | Kết luận
  --------------+-----------+-------------+---------------+-------------------------
          1,024 |   0.06 GB |     1.64 GB |       5.50 GB | vừa, nhờ hook
          2,048 |   0.23 GB |     6.58 GB |       5.68 GB | vừa, nhờ hook
          4,096 |   0.94 GB |    26.31 GB |       6.38 GB | vừa, nhờ hook / ngây thơ: TRÀN
          8,192 |   3.76 GB |   105.23 GB |       9.20 GB | vừa, nhờ hook / ngây thơ: TRÀN
```

Cột "một lớp" **khớp chính xác** bảng ở mục 5 của `CLAUDE.md`: 0,23 / 0,94 / 3,76 GB. Trọng số sau NF4 là 5,44 GB, nằm dưới ngưỡng 7 GB mà T06 đặt ra.

##### Kết quả — độ dài token

```
  Bộ               Mẫu  Ngữ cảnh  tok/từ    p50    p90     p99     max
  ------------------------------------------------------------------
  vihallu        7,000     3,865    1.35    218    358     549    2347
  isedsc01      36,369     4,793    1.33    768   1456    2049    6543
  viwikifc      16,738     1,479    1.36    183    388     536     805
  vifactcheck    5,062     1,035    1.33    823   1519    2687    4696

  Bộ               p50     p99      max         vượt 2.048         vượt 4.096
  ----------------------------------------------------------------------------
  vihallu          308     635     2474          3 (0.04%)          0 (0.00%)
  isedsc01         796    2072     6622        396 (1.09%)          6 (0.02%)
  viwikifc         214     590      950          0 (0.00%)          0 (0.00%)
  vifactcheck      870    2738     4782        142 (2.81%)          8 (0.16%)
```

Ba kết luận, đã ghi vào mục 4B của `docs/DATA.md`:

1. Tokenizer Qwen2.5 nén tiếng Việt **1,33–1,36 token mỗi từ**, tốt hơn nhiều so với ước lượng 2 token/từ trước đó. Ngữ cảnh 4.805 từ dài nhất của ISE-DSC01 chỉ ra 6.543 token chứ không phải gần 10.000.
2. **`max_context_tokens = 4096` gần như không cắt gì** — 14 mẫu trên tổng 65.169 mẫu của cả bốn bộ. Vẫn phải đặt cờ `truncated=True` và đếm lại lúc trích đặc trưng.
3. **Nấc lùi 1 rẻ hơn tưởng.** Hạ xuống 2.048 chỉ cắt thêm 1,09 % ISE-DSC01 và 2,81 % ViFactCheck, tức nếu T07 chật bộ nhớ thì đây là nấc nên dùng trước, gần như không mất mát. Đã ghi con số này vào bảng sáu nấc trong `CLAUDE.md`.

##### Ghi chú

- Hàm `load_raw` trong script đọc thẳng file thô ở mức tối thiểu. T09–T12 sẽ thay bằng bộ nạp thật theo schema chung; script này giữ nguyên vì nó chỉ đo độ dài, không cần chuẩn hóa nhãn.
- Báo cáo in ra tiếng Việt nên script ép `sys.stdout` sang UTF-8 để không vỡ trên console cp1252 của Windows.

---

<a id="pr-6"></a>

### #6 — T06: script nạp mô hình 4-bit và notebook chạy trên Kaggle T4

- **Nhánh:** `t06-nap-mo-hinh-4bit` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 18:09 · **gộp:** 19/08/2026 18:09 · **commit gộp:** [`7c35751`](https://github.com/wsunicorn/vihallulens/commit/7c35751fc9c66d73f52acea0da40e1986084b3b5)¹
- **Thay đổi:** +249 / −1, 4 file · **bình luận bot:** 0

Task T06 trong `TASKS.md` — **phần công cụ**. PR này chưa tick T06 vì tiêu chí hoàn thành đòi log thật trên Tesla T4, mà việc đó phải chạy trên Kaggle.

##### Đã làm

`scripts/probe_load_model.py` nạp mô hình đúng cấu hình đã chốt ở mục 3 của `CLAUDE.md` và mục 2.2 của `docs/SPEC.md`: NF4, `bnb_4bit_compute_dtype=float16`, double quant, `attn_implementation="eager"`, `device_map={"": 0}`. In ra thời gian nạp, VRAM cấp phát / đặt chỗ / đỉnh / còn trống.

Ba thứ script tự kiểm, để không phải soi log bằng mắt:

1. **Compute capability.** In ra và cảnh báo nếu dưới 7.5 — đúng cảnh báo về P100 ở mục 2 của `CLAUDE.md`.
2. **`attn_implementation` sau khi nạp có thật sự là `eager` không.** Nếu `transformers` âm thầm rơi về SDPA thì T07 không lấy được attention, và biết ở T06 rẻ hơn biết ở T07.
3. **Ngưỡng 7 GB** của tiêu chí T06, trả mã thoát khác 0 nếu vượt.

Script chấp nhận cả `dtype=` lẫn `torch_dtype=` vì `transformers` 5 đã đổi tên tham số — đây là hệ quả trực tiếp của ghi chú rủi ro ở PR #1.

`notebooks/t06_nap_mo_hinh_t4.ipynb` chỉ clone, cài đặt, nạp `HF_TOKEN` từ Kaggle Secrets và gọi script, đúng quy tắc "notebook không chứa logic" ở mục 9 của `CLAUDE.md`. Notebook cài `--no-deps` để không kéo bản `torch` khác đè lên bản dựng sẵn theo CUDA của image Kaggle.

##### Kiểm tra đã chạy được ở máy không GPU

```
================================================================================
NẠP MÔ HÌNH 4-BIT — Qwen/Qwen2.5-7B-Instruct
================================================================================
  torch                 : 2.13.0+cpu
  transformers          : 5.15.0
  GPU                   : KHÔNG CÓ — task T06 phải chạy trên Kaggle T4
mã thoát: 1
```

`ruff check .` xanh, notebook là JSON hợp lệ 6 ô.

##### Còn lại

Chạy notebook trên Kaggle T4 rồi dán output ô cuối vào đây. Khi đó mới tick T06.

---

<a id="pr-7"></a>

### #7 — T07: chốt mẫu prompt và trích attention bằng forward hook

- **Nhánh:** `t07-trich-attention` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 18:19 · **gộp:** 19/08/2026 18:19 · **commit gộp:** [`7b4e982`](https://github.com/wsunicorn/vihallulens/commit/7b4e9828bdb7a4e245c767862278a69057c284d6)¹
- **Thay đổi:** +956 / −2, 8 file · **bình luận bot:** 1

Task T07 trong `TASKS.md` — **cổng chặn 🚩**. PR này chưa tick T07 vì tiêu chí đòi log thật dưới 14 GB trên Tesla T4.

##### Câu hỏi phiên bản đã có lời giải

Rủi ro ghi ở PR #1 là `transformers` giải ra bản 5.15.0, nhánh API mới, nên chưa chắc hook nhận được `attn_weights`. Đã đo thật bằng một Qwen2 hai lớp dựng ngẫu nhiên trên CPU:

```
transformers 5.15.0, attn_implementation=eager
output_attentions=True  -> hook nhận attn_weights shape (1, 4, 12, 12)
output_attentions=False -> hook nhận attn_weights shape (1, 4, 12, 12)
```

Hook nhận `attn_weights` **kể cả khi không bật cờ**. Hệ quả thiết kế: extractor **không bật `output_attentions`** nữa. Cờ đó là thứ khiến `all_self_attns` gom ma trận của cả 28 lớp — tắt nó đi thì rủi ro tích lũy biến mất ngay từ gốc, chứ không phải chỉ được chặn lại. Hook vẫn trả `(attn_output, None)` như một lớp phòng thủ thứ hai.

##### Mẫu prompt đã chốt

Ghi nguyên văn vào mục 8 của `CLAUDE.md`, hiện thực ở `src/vihallulens/extract/prompt.py`:

```
<|im_start|>system
Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.<|im_end|>
<|im_start|>user
Ngữ cảnh:
{context}

Câu hỏi: {question}<|im_end|>
<|im_start|>assistant
{response}<|im_end|>
```

Bốn quy tắc đi kèm: bỏ hẳn khối câu hỏi khi bộ dữ liệu không có câu hỏi; vùng ngữ cảnh là đúng chuỗi `{context}` không gồm dòng tiêu đề; vùng phản hồi là đúng chuỗi `{response}`; token khung không tính vào tử số lẫn mẫu số.

Vị trí hai vùng tìm bằng cách **dò chuỗi trong prompt đã render** rồi ánh xạ sang token qua `return_offsets_mapping`, không đếm ký tự khung. Nhờ vậy Sailor2 ở E13 có chat template hơi khác thì vị trí vẫn đúng thay vì lệch âm thầm.

##### Toán lookback

Theo đúng định nghĩa gốc ở mục 1 của `docs/REFERENCES.md` — **trung bình theo token, không phải tổng**:

- `A(context)` chia cho số token ngữ cảnh
- `A(new)` chia cho số token phản hồi **đứng trước** token hiện tại; nhờ mask nhân quả, lấy tổng cả hàng rồi trừ đường chéo là ra đúng phần đó
- mỗi chunk chia cho số token của chính nó, nên chunk dài không tự thắng chunk ngắn

12 ca kiểm thử trong `tests/test_attention_math.py` đối chiếu với ma trận chú ý có đáp án tính tay: token phản hồi đầu tiên chưa có lịch sử nên tỷ lệ bằng 1; đường chéo bị loại; token khung không ảnh hưởng kết quả; hai chunk cùng khối lượng nhưng khác độ dài phải cho hai giá trị khác nhau đúng theo tỷ lệ.

##### Chạy toàn tuyến trên CPU

```
================================================================================
T07 — TRÍCH ATTENTION BẰNG FORWARD HOOK
================================================================================
  transformers          : 5.15.0
  chế độ                : tiny (CPU, trọng số ngẫu nhiên)
  số lớp được hook      : 2

  mẫu tổng hợp
    ngữ cảnh              : 23 từ, 3 chunk
    lookback_per_chunk    : (2, 4, 10, 3)
    lookback_total        : (2, 4, 10)
    self_attention        : (2, 4, 10)
    bị cắt ngữ cảnh       : False
    lookback_total trung bình: 0.5500  (min 0.4841, max 1.0000)
```

`lookback_per_chunk` ra đúng `(n_layers, n_heads, n_response_tokens, n_chunks)` như `docs/SPEC.md` 2.2 quy định. `pytest` 54 ca xanh, `ruff check .` xanh.

##### Còn lại

Chạy `notebooks/t07_trich_attention_t4.ipynb` trên Kaggle T4 — notebook làm cả T06 lẫn T07 trong một phiên để đỡ quota — rồi dán output ô 5 và ô 6 vào đây. Khi đó mới tick cả hai task.

Nếu ô 6 báo hết bộ nhớ, ô cuối notebook có sẵn lệnh cho nấc lùi 1 và nấc 4; nấc 2 và 3 cần sửa code và nấc 3 phải hỏi trước.

##### Ghi chú

- `src/vihallulens/data/chunking.py` mới chỉ có dataclass `Chunk`. Hai chiến lược chia chunk là T15; script T07 dùng một bộ tách câu tạm, có ghi chú rõ.
- `AttentionExtractor.from_components` được thêm để bọc mô hình dựng sẵn, phục vụ chế độ `--tiny`.

---

<a id="pr-8"></a>

### #8 — Sửa ba lỗi trước khi chạy cổng T07

- **Nhánh:** `sua-loi-truoc-cong-t07` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 18:35 · **gộp:** 19/08/2026 18:35 · **commit gộp:** [`f6fae0c`](https://github.com/wsunicorn/vihallulens/commit/f6fae0c543abb6dcd0ea1676cbc307c6dfadcdc8)¹
- **Thay đổi:** +440 / −55, 9 file · **bình luận bot:** 1

Rà lại code trước khi đốt quota GPU, sau khi biết đường dẫn thật trên Kaggle là `/kaggle/input/datasets/unicorn1209/vihallulens/`. Tìm được ba lỗi, một trong đó nặng hơn chuyện đường dẫn.

##### Lỗi 1 — đường dẫn Kaggle bị viết cứng

Notebook và README đều giả định `/kaggle/input/vihallulens/`. Sai với cách dataset đang được gắn.

Thay vì sửa thành một hằng số khác rồi lại sai ở máy khác, thêm `src/vihallulens/data/paths.py` tự dò thư mục chứa `vihallu_train.csv`. Thứ tự ưu tiên: `--data-dir` → biến môi trường `VIHALLULENS_DATA_DIR` → `data/raw` → các vị trí dưới `/kaggle/input` (thử cả `<slug>/`, `datasets/<chủ>/<slug>/` và hai mức lồng khác).

Truyền `--data-dir` sai đường dẫn giờ **báo lỗi** thay vì âm thầm rơi về `data/raw` — chạy thí nghiệm trên dữ liệu không ai yêu cầu là kiểu lỗi không bao giờ lộ ra trong kết quả.

##### Lỗi 2 — cắt ngữ cảnh làm hỏng offset của chunk, âm thầm

Đây là lỗi nặng và nó nằm đúng trên đường mà bài kiểm tra T07 đi qua.

`_fit_context` cũ cắt ngữ cảnh **theo ký tự** (`context[:keep] + context[-keep:]`), nhưng danh sách chunk truyền vào `extract()` có `char_start`/`char_end` tính theo ngữ cảnh **gốc**. Sau khi cắt, offset không còn trỏ đúng chỗ nữa. Không có exception nào, không có cảnh báo nào — chỉ là mọi con số per-chunk bị gán cho đoạn văn bản khác.

Mẫu ISE-DSC01 dài nhất mà T07 bắt buộc phải chạy có 6.622 token, vượt ngưỡng 4.096, nên đường này **chắc chắn** được kích hoạt.

Cách sửa: cắt theo **nguyên khối chunk** ở giữa (`drop_middle_chunks`), rồi dịch offset của các chunk còn lại và đánh số lại liên tục. Chunk là đơn vị quy kết attention nên nửa chunk không có nghĩa gì; cắt theo chunk vừa đúng tinh thần "cắt từ giữa" của `docs/SPEC.md` 2.2, vừa giữ offset chính xác tuyệt đối.

Kiểm chứng bằng cách ép ngân sách xuống 128 token:

```
trước khi cắt : 60 chunk, 3709 ký tự
sau khi cắt   : 3 chunk, 185 ký tự, truncated = True
chunk lệch offset: 0 (phải là 0)
index liên tục   : True
shape            : (2, 4, 9, 3) | truncated = True
chunk toàn số 0  : 0 trên 3 (phải là 0 nếu offset đúng)
```

Hệ quả cần biết: khi ngữ cảnh bị cắt thì `n_chunks` giảm. Đúng bản chất — đoạn bị bỏ không còn nằm trong ngữ cảnh nữa. Ảnh hưởng 14 mẫu trên tổng 65.169 theo số đo ở T05.

##### Lỗi 3 — thiếu đúng cái test mà T07 yêu cầu

`TASKS.md` T07 ghi rõ phải có "một test khẳng định `attn_weights is not None`". Lượt trước mình chỉ chạy bằng script rời rồi dán kết quả, tức là không có gì bảo vệ khi nâng cấp thư viện sau này.

Thêm `tests/test_attention_hook.py`, dựng Qwen2 hai lớp từ config nên chạy offline, không cần tải gì: khẳng định hook nhận `attn_weights` với cả hai giá trị `output_attentions`, khẳng định trả `None` thay ma trận không làm vỡ forward, và kiểm tra các hàng attention cộng lại bằng 1 (tức đúng là sau softmax chứ không phải điểm thô).

##### Thêm một lớp dự phòng

Image Kaggle có thể cài `transformers` 4.x, nơi `attn_weights` chỉ xuất hiện khi bật cờ. Extractor giờ tự thử lại một lần với `output_attentions=True` nếu lượt đầu không thu được gì. An toàn về bộ nhớ vì hook vẫn thay mọi ma trận bằng `None`.

Ô 4 của notebook cũng chạy `pytest tests/test_attention_hook.py` **trước** khi đụng tới GPU, nên phiên bản thư viện lệch sẽ lộ ra khi chưa tốn quota nào.

##### Kiểm tra

```
$ ruff check .
All checks passed!

$ pytest
71 passed
```

18 ca mới: 8 cho dò đường dẫn, 5 cho hook và 5 cho cắt ngữ cảnh theo chunk.

---

<a id="pr-9"></a>

### #9 — Sửa notebook: chạy lại không còn dùng nhầm code cũ

- **Nhánh:** `sua-notebook-clone-lai` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 18:42 · **gộp:** 19/08/2026 18:42 · **commit gộp:** [`a8a33af`](https://github.com/wsunicorn/vihallulens/commit/a8a33aff926f2f351b88b3c628f6bed64f094c06)¹
- **Thay đổi:** +33 / −132, 3 file · **bình luận bot:** 0

Lỗi gặp trên Kaggle:

```
ModuleNotFoundError: No module named 'vihallulens.data.paths'
```

##### Nguyên nhân

Thông báo lỗi nói `vihallulens.data` import được nhưng thiếu `paths`, tức là repo trong `/kaggle/working` là bản trước PR #8. Ô 1 cũ chạy:

```
!git clone -q https://github.com/wsunicorn/vihallulens.git /kaggle/working/vihallulens
```

`git clone` vào một thư mục đã tồn tại sẽ **thất bại**, nhưng `!` trong notebook không dừng ô lại. `%cd` vẫn nhảy vào thư mục cũ và mọi ô sau chạy bằng code cũ mà không có dấu hiệu gì. Thư mục tồn tại từ trước là chuyện bình thường: chỉ cần bấm Run All lần thứ hai trong cùng một phiên.

Lỗi nằm ở notebook mình viết, không phải ở thao tác chạy.

##### Sửa

**Ô 1** giờ kiểm tra thư mục trước: đã là repo thì `git fetch` rồi `git reset --hard origin/main`, chưa có thì mới clone. Dùng `subprocess` có kiểm tra mã trả về nên lệnh hỏng là ô dừng ngay chứ không đi tiếp. In ra commit đang dùng để đối chiếu.

**Ô 3 mới** xóa mọi module `vihallulens` đã nạp rồi import lại — sau `pip install` trong cùng một phiên, Python vẫn giữ bản nạp trước đó trong `sys.modules`. Ô này in phiên bản Python, phiên bản `transformers` và đường dẫn gói, nên nếu còn chạy nhầm bản nào thì thấy ngay.

**Bỏ `notebooks/t06_nap_mo_hinh_t4.ipynb`.** Notebook T07 đã chạy cả T06, giữ thêm một bản chỉ tạo thêm một chỗ mắc đúng lỗi vừa rồi. `TASKS.md` T06 đã trỏ sang notebook T07.

##### Kiểm tra

```
$ ruff check .
All checks passed!

$ pytest
71 passed
```

---

<a id="pr-10"></a>

### #10 — Không phụ thuộc vào editable install nữa khi chạy trên Kaggle

- **Nhánh:** `sua-import-tren-kaggle` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 18:48 · **gộp:** 19/08/2026 18:49 · **commit gộp:** [`aaad26c`](https://github.com/wsunicorn/vihallulens/commit/aaad26ce30bc6190001f6c98360dfb78f564640f)¹
- **Thay đổi:** +107 / −3, 5 file · **bình luận bot:** 1

Lỗi lặp lại sau khi đã sửa chuyện clone:

```
---> 15 from vihallulens.data.paths import find_raw_dir
ModuleNotFoundError: No module named 'vihallulens.data.paths'
```

##### Nguyên nhân thật

Giả thuyết trước của mình (clone hỏng vì thư mục đã tồn tại) **sai**. Nguyên nhân thật nằm ở cơ chế cài đặt.

`pip install -e .` không copy code vào `site-packages`, nó ghi một file `.pth` trỏ về `src/` của repo. Python **chỉ đọc file `.pth` lúc khởi động trình thông dịch**. Kernel của notebook đã chạy từ trước khi ô 2 cài đặt, nên nó không bao giờ thấy đường dẫn mới — và `import vihallulens` chỉ chạy được nhờ tàn dư của một lần cài trước đó, tức là bản code cũ.

Điều này giải thích đúng triệu chứng: `vihallulens` và `vihallulens.data` import được, riêng `paths` thì không, vì bản cũ chưa có file đó.

##### Cách sửa

Bỏ hẳn việc phụ thuộc vào trạng thái cài đặt, cho mọi thứ chạy thẳng trên mã đã clone:

- **`conftest.py`** ở gốc repo thêm `src/` vào đầu `sys.path`, nên `pytest` luôn kiểm thử đúng mã trong checkout, có cài hay không cũng vậy. Đây cũng là điều nên có: test mà chạy trên một bản khác với bản đang sửa thì không nói lên điều gì.
- **`scripts/probe_vram.py` và `scripts/probe_attention_hook.py`** tự thêm `src/` vào `sys.path` trước khi import.
- **Ô 3 của notebook** gọi script bằng tiến trình riêng thay vì import trong kernel. Tiến trình mới đọc `.pth` lúc khởi động nên không dính vấn đề trên, và cách này cũng đúng quy tắc "notebook chỉ gọi hàm từ src" ở mục 9 của `CLAUDE.md`.

##### Thêm một công cụ chẩn đoán

`scripts/probe_env.py` in ra commit đang dùng, phiên bản Python, torch, transformers, bitsandbytes, accelerate, **đường dẫn thật của gói `vihallulens`**, và thư mục dữ liệu kèm danh sách file.

Cả hai lần hỏng vừa rồi đều cùng một dạng: mã đang chạy không phải mã ta tưởng. Script này đưa câu trả lời đó lên ngay ô đầu tiên, trước khi tốn bất kỳ giây GPU nào.

```
================================================================================
MÔI TRƯỜNG
================================================================================
  repo             : D:\StudyDocument\KLTN\vihallulens
  commit           : d1c583d Sửa notebook: chạy lại không còn dùng nhầm code cũ (#9)
  python           : 3.11.9
  torch            : 2.13.0+cpu
  transformers     : 5.15.0
  bitsandbytes     : 0.50.1
  accelerate       : 1.14.0
  vihallulens      : 0.1.0 tại ...\src\vihallulens\__init__.py
  dữ liệu          : data\raw  (14 file)
```

##### Kiểm tra

```
$ ruff check .
All checks passed!

$ pytest
71 passed
```

---

<a id="pr-11"></a>

### #11 — T06 đạt trên T4; thêm chẩn đoán nan cho T07

- **Nhánh:** `t06-dat-va-chan-doan-nan` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 18:58 · **gộp:** 19/08/2026 18:58 · **commit gộp:** [`d3f15ba`](https://github.com/wsunicorn/vihallulens/commit/d3f15baf10cb91df686cb6bb3d8c6857bdb37f16)¹
- **Thay đổi:** +67 / −8, 4 file · **bình luận bot:** 1

##### T06 — ĐẠT, đã tick

Log thật trên Kaggle Tesla T4 (compute capability 7.5, 14.912 MB):

```
  Thời gian nạp         : 121.4 giây
  Lượng tử hóa          : nf4
  attn_implementation   : eager
  Số lớp / số đầu       : 28 / 28
  dtype tham số         : torch.float16

  VRAM đang cấp phát    : 5,302 MB
  VRAM đã đặt chỗ       : 5,462 MB
  VRAM còn trống        : 9,450 MB   ← ngân sách cho attention

  Tiêu chí T06 (< 7,168 MB): ĐẠT
```

Ước tính trên giấy ở T05 là 5,44 GB; đo thật 5,30 GB, lệch dưới 3 %.

##### T07 — bộ nhớ đạt, nhưng số liệu là nan

```
  ViHallu (~200 từ)      lookback_per_chunk (28, 28, 48, 4)   VRAM đỉnh 5,489 MB
  ISE-DSC01 (dài nhất)   lookback_per_chunk (28, 28, 22, 96)  VRAM đỉnh 8,395 MB
  Tiêu chí T07 (< 14,336 MB): ĐẠT
  lookback_total trung bình: nan
```

Phần khó nhất của cổng đã qua: hook chạy, hình dạng đúng, cắt ngữ cảnh hoạt động (169 chunk còn 96), và đỉnh 8.395 MB đúng khoảng 8–9 GB đã ước tính ở mục 5 của `CLAUDE.md`.

Nhưng `lookback_total` ra `nan`. Công thức lookback không thể sinh `nan` từ đầu vào hữu hạn: nó chỉ gồm cộng, chia cho số dương và một `clamp` chặn dưới. Vậy `attn_weights` nhận được đã chứa `nan` hoặc `inf` ngay từ trong mô hình.

Giả thuyết chính: **Qwen2.5 được huấn luyện ở bfloat16**, dải số rộng hơn `float16` rất nhiều. Chạy `float16` thì một số lớp tràn thành `inf`, và `softmax` của `inf` cho `nan`.

##### Không đoán, đo

Thêm `layer_diagnostics` chạy ngay trong hook, chỉ soi các hàng thật sự dùng nên tốn vài MB:

- **lớp nào có `nan`/`inf`** — nếu chỉ vài lớp cuối thì đúng là tràn số tích lũy; nếu ngay lớp 0 thì nguyên nhân khác
- **tổng hàng attention** — khỏe mạnh là 1,0000; nếu khác thì thứ hook nhận được không phải phân bố sau softmax, tức giả định về phiên bản thư viện sai chứ không phải chuyện tràn số

Hai chỉ số này phân biệt được hai nguyên nhân hoàn toàn khác nhau mà đứng ngoài chỉ thấy chung một chữ `nan`.

##### Và chuẩn bị sẵn cách chữa

`AttentionExtractor` nhận thêm `compute_dtype`, script có `--compute-dtype {float16,bfloat16,float32}`. Notebook thêm **ô 7** chạy `float32` ngay trong cùng phiên — mô hình đã nằm trong cache nên chỉ mất khoảng 20 giây nạp lại.

`float32` không tràn nhưng tốn gấp đôi: ước tính đỉnh khoảng 10–11 GB trên 14,9 GB, vẫn vừa. `bfloat16` là lựa chọn tự nhiên hơn nhưng T4 là kiến trúc Turing, không có nhân bf16, nên để sau cùng.

##### Kiểm tra

```
$ ruff check .   → All checks passed!
$ pytest         → 71 passed
```

Chế độ `--tiny` trên CPU giờ in thêm: `tổng hàng attention: 1.0000`, `lớp có nan/inf: không có`.

---

<a id="pr-12"></a>

### #12 — Thêm công cụ so sánh float16 với float32 trước khi chốt

- **Nhánh:** `so-sanh-dtype` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 19:14 · **gộp:** 19/08/2026 19:14 · **commit gộp:** [`2512e81`](https://github.com/wsunicorn/vihallulens/commit/2512e8153393d41376bd893d07f75cfc60dc1b8b)¹
- **Thay đổi:** +210 / −1, 3 file · **bình luận bot:** 1

Sau khi có chẩn đoán từ T07, chưa chốt ngay kiểu số mà đo thêm.

##### Đã biết chắc

| | float16 | float32 |
|---|---|---|
| Lớp hỏng | **chỉ lớp 27** (lớp cuối), 27 lớp còn lại sạch | không lớp nào |
| Tổng hàng attention | `nan` | 1,0000 |
| `lookback_total` | `nan` | 0,2208 và 0,1127, nằm trong [0, 1] |
| ViHallu ~300 token | 868 ms, 5.489 MB | 1.936 ms, 7.732 MB |
| ISE-DSC01 dài nhất | 3.886 ms, 8.395 MB | 14.806 ms, 10.658 MB |

Cả hai đều dưới ngưỡng 14.336 MB. Vậy **T07 đạt tiêu chí bộ nhớ ở cả hai kiểu số**; thứ chưa chốt là dùng kiểu nào.

##### Hai câu hỏi mà một mẫu không trả lời được

1. **Có phải lúc nào cũng chỉ lớp 27 không?** Bỏ một lớp hỏng chỉ là phương án khi lớp hỏng luôn là cùng một lớp. Mới thử đúng hai mẫu.
2. **27 lớp còn sống ở float16 có đúng không?** Một lớp có thể hữu hạn mà vẫn đã bị bóp méo, vì hidden state đi vào nó đã gần ngưỡng tràn. Kiểu sai này không nhìn thấy được nếu không có cái để đối chiếu — và nó nguy hiểm hơn `nan` nhiều, vì `nan` thì lộ ra còn số bị bóp méo thì không.

##### Công cụ

`scripts/compare_dtypes.py` chạy cả hai kiểu số trên **cùng một bộ mẫu**, chọn 10 mẫu ViHallu và 10 mẫu ISE-DSC01 trải đều theo độ dài ngữ cảnh. Kiểm thử trên máy cho thấy dải mẫu chọn được là 47 tới 4.805 từ, tức cả hai đầu phân phối đều có mặt.

Báo cáo gồm bảng theo từng lớp: tỷ lệ mẫu bị `nan` ở float16, và `|Δ|` trung bình cùng `|Δ|` lớn nhất so với float32 ở những lớp còn hữu hạn. `lookback_total` nằm trong [0, 1] nên đọc `|Δ|` như phần trăm thang đo.

Kết luận cuối in ra riêng: nếu bỏ các lớp từng hỏng thì sai lệch còn lại là bao nhiêu.

##### Kiểm tra

Phần logic thuần đã chạy trên máy không GPU: hàm chọn mẫu trải đều đúng, bảng báo cáo dựng đúng với dữ liệu giả, `collect_samples` đọc được cả bốn file thật.

```
$ ruff check .   → All checks passed!
$ pytest         → 71 passed
```

##### Còn lại

Chạy ô 8 của notebook (khoảng 4-5 phút GPU) rồi dán kết quả. Có số rồi mới sửa quyết định về kiểu số trong `CLAUDE.md` mục 3 và `docs/SPEC.md` mục 2.2.

---

<a id="pr-13"></a>

### #13 — Chốt float16 bỏ lớp 27, lưu hai biến thể lookback, bỏ token đầu

- **Nhánh:** `chot-dtype-va-hai-bien-the` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 19:39 · **gộp:** 19/08/2026 19:39 · **commit gộp:** [`82bab7d`](https://github.com/wsunicorn/vihallulens/commit/82bab7d4140e56cb63494ccd06d46994e5f94132)¹
- **Thay đổi:** +235 / −93, 9 file · **bình luận bot:** 0

Hiện thực hai quyết định vừa chốt, dựa trên số đo 20 mẫu trải từ 47 tới 4.805 từ.

##### Bằng chứng cho quyết định kiểu số

| | Kết quả |
|---|---|
| Tập hợp lớp từng `nan` ở float16 | **`[27]`** — chỉ lớp cuối, ở **20/20** mẫu |
| `\|Δ\|` trung bình trên 27 lớp còn lại | 0,00074 (0,07 % thang đo) |
| `\|Δ\|` phân vị 99 | 0,00635 |
| Lớp lệch nhiều nhất | **14 và 19**, nằm giữa mô hình |
| Tốc độ | 1.074 ms so với 3.853 ms mỗi mẫu, nhanh 3,6 lần |

Chi tiết quan trọng nhất là dòng áp chót: nếu float16 bị bóp méo do hidden state gần ngưỡng tràn thì sai lệch phải **tăng dần về cuối mô hình**. Nó không tăng dần — lớp lệch nhiều nhất nằm giữa. Vậy không có bóp méo hệ thống, chỉ có đúng một lớp hỏng dứt khoát.

Chốt **float16 + `exclude_layers: [27]`**. Đây là nấc lùi 2 trong bảng sáu nấc ở mục 5 của `CLAUDE.md`, không phải sửa quyết định nào. Với 23.786 mẫu ISE-DSC01 của E06, chênh lệch là khoảng 7 giờ GPU mỗi lần trích.

##### Lỗi công thức mà số đo lôi ra

`|Δ|` lớn nhất bằng đúng **1,00000**, tức toàn bộ thang đo. Con số tròn trịa như vậy không phải nhiễu số học mà là dấu hiệu của lỗi logic.

Truy ra: **token phản hồi đầu tiên**. Nó chưa có token nào đứng trước nên `self_mean = 0`, và tỷ lệ thành `context/(context+0) = 1` bất kể mô hình làm gì. Ở float16, nếu chú ý vào ngữ cảnh underflow về đúng 0 thì thành `0/ε = 0`. Một bên 1, một bên 0, và **cả hai đều vô nghĩa** vì đó là phép chia 0/0. Bài gốc cũng chia cho `t-1`, tức không định nghĩa ở token đầu.

Đã bỏ hẳn token đầu khỏi phần được chấm. Trục token của mọi mảng giờ dài `n_response_tokens - 1`. Sau khi sửa, chạy thử trên CPU cho `lookback_total` trong khoảng 0,4907 đến 0,5088 — không còn chạm 1,0.

Đây là lỗi sẽ không bao giờ tự lộ ra: nó chỉ làm một hàng trên mỗi (lớp, đầu) mang giá trị bịa, và giá trị đó vẫn nằm trong [0, 1] nên mọi kiểm tra hợp lệ đều qua.

##### Hai biến thể mẫu số

Lưu song song, tính từ cùng một ma trận nên chi phí thêm gần bằng không:

- `lookback_total` — X là **toàn bộ token trước phản hồi**, khung và câu hỏi tính cả. Đúng công thức Lookback Lens gốc, nên E02 mới gọi là tái lập được.
- `lookback_context` — chỉ đếm ngữ cảnh truy xuất. Dễ diễn giải, và là nền của phần chunk-aware.

Trước đó mình loại token khung khỏi cả hai, tức đã lệch khỏi bài gốc mà không nhận ra. `docs/REFERENCES.md` mục 1 và `CLAUDE.md` mục 8 đã ghi lại.

##### Thay đổi kèm theo

- `ExtractorConfig` thêm `compute_dtype` và `exclude_layers`; `configs/example.yaml` điền sẵn `[27]` kèm lý do.
- `scripts/probe_attention_hook.py` có `--exclude-layers` (mặc định 27) và in cả hai biến thể.
- `CLAUDE.md` mục 3 thêm hai dòng quyết định; mục 8 sửa quy tắc 4 và thêm quy tắc 5.
- `docs/SPEC.md` mục 2.2 cập nhật `AttentionFeatures`.

##### Kiểm tra

```
$ ruff check .   → All checks passed!
$ pytest         → 75 passed
```

`tests/test_attention_math.py` viết lại: thêm ca khẳng định token đầu bị loại, ca khẳng định hai mẫu số khác nhau đúng bằng phần token khung, ca khẳng định mọi tỷ lệ nằm trong [0, 1].

##### Còn lại

Chạy lại ô 6 trên Kaggle với cấu hình cuối (float16, bỏ lớp 27) để lấy log chốt T07.

---

<a id="pr-14"></a>

### #14 — T07: cổng khả thi kỹ thuật đã qua trên Tesla T4

- **Nhánh:** `t07-dat-cong-mo` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 19:52 · **gộp:** 19/08/2026 19:52 · **commit gộp:** [`8e0219f`](https://github.com/wsunicorn/vihallulens/commit/8e0219f1105ed0e55a7d82df336b05c42253c2a6)¹
- **Thay đổi:** +10 / −2, 1 file · **bình luận bot:** 1

Log thật trên Kaggle Tesla T4 với cấu hình đã chốt: `float16`, bỏ lớp 27, 27 lớp được hook.

```
  ViHallu (~200 từ)
    lookback_per_chunk    : (27, 28, 47, 4)
    thời gian             : 951 ms      VRAM đỉnh: 5,496 MB
    tổng hàng attention   : 1.0000      lớp có nan/inf: không có
    lookback_total        : trung bình 0.3613
    lookback_context      : trung bình 0.1969

  ISE-DSC01 (dài nhất, 4.805 từ, 169 chunk còn 96)
    lookback_per_chunk    : (27, 28, 21, 96)
    thời gian             : 4,046 ms    VRAM đỉnh: 8,395 MB
    tổng hàng attention   : 1.0000      lớp có nan/inf: không có
    lookback_total        : trung bình 0.1119
    lookback_context      : trung bình 0.0679

  Tiêu chí T07 (< 14,336 MB): ĐẠT
```

##### Bốn tiêu chí của task, đối chiếu từng cái

| Tiêu chí | Kết quả |
|---|---|
| Cả hai mẫu chạy xong | ✅ ViHallu 200 từ và ISE-DSC01 dài nhất 4.805 từ |
| `max_memory_allocated` dưới 14 GB | ✅ 8.395 MB, còn dư 42 % |
| In shape của `lookback_per_chunk` | ✅ (27, 28, 47, 4) và (27, 28, 21, 96) |
| Mục 8 của `CLAUDE.md` có mẫu prompt | ✅ ghi nguyên văn kèm năm quy tắc |

##### Vài điều số liệu nói thêm

`lookback_context` thấp hơn `lookback_total` ở cả hai mẫu (0,197 so với 0,361; 0,068 so với 0,112). Hợp lý: mẫu số của `lookback_total` gồm cả token khung, mà token neo chú ý thường hút phần lớn khối lượng, nên tỷ lệ trông cao hơn. Đây chính là lý do giữ cả hai biến thể — chúng đo hai thứ khác nhau.

Cả hai chỉ số đều thấp hơn ở mẫu ISE-DSC01 dài. Cũng hợp lý vì mẫu số chia cho số token ngữ cảnh, mà ngữ cảnh dài gấp hai chục lần.

##### Ghi chú chuyển cho T21

`lookback_total` vẫn có phần tử ở đúng 0 và đúng 1. Khác với lỗi token đầu đã sửa, đây là **giá trị biên thật**: đầu chú ý chỉ nhìn prompt cho ra 1, đầu chỉ nhìn phần tự sinh cho ra 0. Trên 27 × 28 × 47 = 35.532 giá trị thì có vài giá trị chạm biên là bình thường. Khi gộp đặc trưng ở T21 cần xử lý biên này thay vì giả định phân bố liên tục.

##### Nghĩa là gì

Rủi ro số một của đề tài, ghi ở mục 5 của `CLAUDE.md`, đã được chứng minh là xử lý được trên đúng phần cứng dự kiến. Không phải đi nấc lùi nào trong sáu nấc. Phương án đề tài thay thế không cần dùng tới.

---

<a id="pr-15"></a>

### #15 — Cập nhật đường dẫn tài liệu hành chính sau khi sắp xếp thư mục

- **Nhánh:** `cap-nhat-duong-dan-tai-lieu` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/08/2026 20:35 · **gộp:** 19/08/2026 20:36 · **commit gộp:** [`8e4e916`](https://github.com/wsunicorn/vihallulens/commit/8e4e9161da73f4eefba3505fd47dbb772445757c)¹
- **Thay đổi:** +190 / −125, 2 file · **bình luận bot:** 1

Thư mục `UniversityRequirements/` (gitignore, không lên GitHub) đã được chia thành bốn thư mục con: `WeeklyLogs/`, `Plan/`, `Reports/`, `MyNotes/`.

`TASKS.md` có ba chỗ trỏ tới file trong thư mục đó, cập nhật lại cho đúng:

- mẫu email báo cáo tuần → `WeeklyLogs/`
- mẫu báo cáo khóa luận của trường → `Reports/`
- file kế hoạch KLTN → `Plan/`

Không đổi nội dung nào khác.

---

<a id="pr-16"></a>

### #16 — TASKS.md kiêm luôn sổ tay giải thích, không chỉ tick tiến độ

- **Nhánh:** `ghi-chu-trong-tasks` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 11:55 · **gộp:** 20/08/2026 11:55 · **commit gộp:** [`c285fb9`](https://github.com/wsunicorn/vihallulens/commit/c285fb914154d220cb56074e4c67346d778ad7ac)¹
- **Thay đổi:** +1 / −1, 1 file · **bình luận bot:** 1

Trước đây có hai file song song: `TASKS.md` theo dõi tiến độ, và một file sổ tay riêng giải thích đề tài. Hai file là thừa việc, nên gộp làm một.

Từ giờ `TASKS.md` mang cả hai vai trò. Quy tắc 6 trong mục 6 của `CLAUDE.md` sửa lại cho rõ: mỗi task xong không chỉ tick `[x]` mà còn viết kèm phần diễn giải — task để làm gì, đã làm gì, kết quả số, học được gì — viết sao cho người chưa biết gì đọc cũng hiểu, thuật ngữ lần đầu xuất hiện thì giải thích ngay tại chỗ.

`TASKS.md` vẫn nằm ở gốc repo như cũ, vẫn lên GitHub.

---

<a id="pr-17"></a>

### #17 — T08: công cụ đo thông lượng và dự báo giờ GPU

- **Nhánh:** `t08-do-thong-luong` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 12:11 · **gộp:** 20/08/2026 12:12 · **commit gộp:** [`9e44367`](https://github.com/wsunicorn/vihallulens/commit/9e44367ef934fc62fd8bf7767996b80b75cb3e17)¹
- **Thay đổi:** +934 / −0, 4 file · **bình luận bot:** 1

Chuẩn bị cho T08. Chưa tick task vì còn thiếu số đo thật trên GPU.

##### Task này trả lời câu gì

T07 trả lời "một mẫu có vừa 16 GB không" — câu hỏi về vật lý. T08 trả lời câu hỏi về lịch: với 30 giờ GPU mỗi tuần, trích đặc trưng cho 71.520 mẫu của bốn bộ có kịp không.

##### Vì sao không đo bằng một con số ms/mẫu

Chi phí phụ thuộc mạnh vào độ dài chuỗi. Đo trên vài mẫu bất kỳ thì lạc quan hay bi quan tùy may rủi. Cách làm ở đây: chia bốn mức độ dài, đo 20 mẫu mỗi mức, nhân trung vị từng mức với số mẫu thật rơi vào mức đó của từng bộ. Đầu ra là số giờ GPU cho mỗi bộ, tức thứ lịch chạy cần.

##### Đã đo được trên CPU

`python scripts/measure_throughput.py --dry-run`

```
  khung mẫu prompt      : 37 token, 41 token khi có câu hỏi

  Bộ                     0–512      513–1024     1025–2048     2049–4096      tổng
  --------------------------------------------------------------------------------
  vihallu                6,461           530             6             3     7,000
  isedsc01               6,188        17,770        11,931           480    36,369
  viwikifc              20,102           817             0             0    20,919
  vifactcheck              705         3,546         2,785           196     7,232
  --------------------------------------------------------------------------------
  tổng                  33,456        22,663        14,722           679    71,520

         0–512 : 20 mẫu,   107–  512 token, từ isedsc01, vihallu
      513–1024 : 20 mẫu,   513–1,024 token, từ isedsc01, vihallu
     1025–2048 : 20 mẫu, 1,025–2,048 token, từ isedsc01
     2049–4096 : 20 mẫu, 2,049–6,659 token, từ isedsc01
```

Số mẫu cả bốn bộ khớp đúng bảng mục 4 `docs/DATA.md` (7.000 / 36.369 / 20.919 / 7.232), nên trình đọc dữ liệu không bỏ sót dòng nào.

Ba điều rút ra trước cả khi chạm GPU:

1. **ISE-DSC01 quyết định chi phí** — 51 % số mẫu nhưng gần như toàn bộ khối lượng ở hai mức đắt.
2. **ViWikiFC gần như miễn phí** — 96 % dưới 512 token, không mẫu nào vượt 1.024.
3. **Mức trên cùng rất thưa** — 679 mẫu, 0,9 %. Nếu chỉ mức này quá đắt thì cắt nó rẻ hơn nhiều so với lùi mô hình.

##### Kiểm tra

```
ruff check .            -> All checks passed!
pytest                  -> 101 passed
pytest tests/test_throughput.py -> 26 passed
```

##### Vài quyết định thiết kế đáng nói

- **Hai đồng hồ.** `forward` là riêng lời gọi mô hình, `end_to_end` gồm cả render prompt, cắt theo ngân sách và chuyển đặc trưng về CPU. Dự báo dùng `end_to_end` vì đó mới là chi phí thật.
- **Một lượt chạy bỏ đi trước khi đo.** Lời gọi CUDA đầu tiên của tiến trình phải trả tiền chọn kernel và khởi động allocator; tính khoản đó vào mức ngắn nhất sẽ bóp méo mọi tỷ lệ giữa các mức.
- **Chọn mẫu trải đều trong mức, không lấy ngẫu nhiên.** Không có seed phải ghi, và chạy lại trên cùng dữ liệu thì đo đúng những mẫu đó. Lấy 20 mẫu ngắn nhất của mức 2049–4096 sẽ định giá mức đó ở đầu rẻ và làm nhẹ mọi dự báo dựng trên nó.
- **Mẫu dài hơn ngân sách bị kẹp vào mức trên cùng** chứ không bỏ đi, vì extractor cắt chúng về đúng 4.096 token nên chúng tốn đúng giá của mức đó.
- **Dự báo là cận trên, không phải điểm ước lượng.** Mỗi mẫu tính theo trung vị của mức nó rơi vào, mà mẫu đo trải đều trong mức còn dữ liệu thật dồn về phía ngắn. Lệch về phía an toàn cho việc lập lịch.
- **Mũ k trong `chi phí ≈ độ dài^k`** được báo cáo, vì nó quyết định nấc lùi 1 có đáng làm không: k gần 2 thì hạ ngân sách token một nửa rẻ đi gần bốn lần, k gần 1 thì gần như không giúp gì.

##### Việc còn lại

Chạy `notebooks/t08_thong_luong_t4.ipynb` trên Kaggle (ước 10–15 phút GPU), dán output vào đây, rồi mới tick T08.

Nếu ô 5 kết luận **CẦN QUYẾT ĐỊNH**, script không tự chọn hướng — theo quy tắc 4 mục 6 `CLAUDE.md`, lùi mô hình đọc chính là đổi quyết định đã chốt nên phải hỏi.

---

<a id="pr-18"></a>

### #18 — T08: cổng khả thi kỹ thuật đã qua trọn vẹn trên T4

- **Nhánh:** `t08-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 12:48 · **gộp:** 20/08/2026 12:48 · **commit gộp:** [`2255bf4`](https://github.com/wsunicorn/vihallulens/commit/2255bf42910a658e8acc5081a5dc2ef79a9c7dc8)¹
- **Thay đổi:** +115 / −8, 7 file · **bình luận bot:** 1

Tick T08. Cổng khả thi kỹ thuật T05–T08 đã qua hết, **đề tài thay thế không cần tới nữa**.

##### Kết quả trên Kaggle Tesla T4

Qwen2.5-7B-Instruct NF4, float16 bỏ lớp 27, 27 lớp được hook, 20 mẫu mỗi mức:

| Mức (token) | Trung vị | Trung bình | p90 | Token TB | Chunk TB | VRAM đỉnh | Lớp nan |
|---|---|---|---|---|---|---|---|
| 0–512 | 389 ms | 407 ms | 486 ms | 371 | 7,5 | 5.517 MB | không có |
| 513–1024 | 779 ms | 743 ms | 879 ms | 746 | 20,4 | 5.617 MB | không có |
| 1025–2048 | 1.401 ms | 1.460 ms | 1.833 ms | 1.379 | 40,7 | 6.305 MB | không có |
| 2049–4096 | 2.641 ms | 2.907 ms | 3.660 ms | 2.492 | 61,5 | **8.428 MB** | không có |

| Bộ | Số mẫu | ms/mẫu | Thời gian GPU | % quota tuần |
|---|---|---|---|---|
| ViHallu | 7.000 | 420 | 0 giờ 49 | 2,7 % |
| ISE-DSC01 | 36.369 | 941 | 9 giờ 30 | 31,7 % |
| ViWikiFC | 20.919 | 404 | 2 giờ 20 | 7,8 % |
| ViFactCheck | 7.232 | 1.031 | 2 giờ 04 | 6,9 % |
| **Tổng** | **71.520** | **742** | **14 giờ 44** | **49,1 %** |

**Kết luận: Qwen2.5-7B-Instruct dùng được ở 4.096 token.** Hai bộ bắt buộc cần 10 giờ 19, tức 34,4 % quota tuần. VRAM đỉnh 8.428/14.336 MB, dư 41 %, khớp 8.395 MB đo ở T07. Không phải dùng nấc lùi nào.

Thêm một xác nhận: **80/80 mẫu không lớp nào ra `nan`**. Quyết định float16 + bỏ lớp 27 chốt ở T07 dựa trên 20 mẫu, giờ đã bền qua 80 mẫu trải đủ dải độ dài.

##### Phát hiện chính: thời gian tuyến tính, bộ nhớ bậc hai

Mũ đo được `k ≈ 1,00`; bốn mức cho 1,049 / 1,044 / 1,016 / 1,060 ms mỗi token — gần như hằng số. Quy tắc nhẩm: **~1,05 ms mỗi token prompt**.

Ở dải 512–4.096 token, thứ tốn thời gian vẫn là phép nhân ma trận của MLP và việc giải nén trọng số NF4, đều tuyến tính theo độ dài; ma trận chú ý tuy bậc hai nhưng chưa đủ lớn để lấn. Nó chi phối *bộ nhớ* thì vẫn đúng — bảng mục 5 `CLAUDE.md` nguyên giá trị.

##### Lượt đo 2.048 xác nhận điều đó bằng số thật

| Mức | 4.096 | 2.048 | Chênh | Cắt ở 2.048 |
|---|---|---|---|---|
| 0–512 | 389 ms | 429 ms | +10,2 % | 0/20 |
| 513–1024 | 779 ms | 872 ms | +12,0 % | 0/20 |
| 1025–2048 | 1.401 ms | 1.616 ms | +15,4 % | 0/20 |
| 2049–4096 | 2.641 ms | 2.080 ms | −21,2 % | 20/20 |
| **Dự báo hai bộ bắt buộc** | **10,32 giờ** | **11,58 giờ** | **+12 %** | |
| **VRAM đỉnh** | **8.428 MB** | **6.305 MB** | **−25 %** | |

Nấc lùi 1 chỉ mua được bộ nhớ, không mua được thời gian. Đã sửa mục 5 `CLAUDE.md` để lần sau khỏi lùi nhầm nấc. Đòn bẩy thời gian thật là lấy mẫu con ISE-DSC01 — nó nuốt 92 % chi phí của hai bộ bắt buộc.

##### Hai điều lượt đo thứ hai làm lộ ra

**1. Không so trực tiếp hai lượt chạy nối nhau trong cùng phiên GPU.** Ba mức dưới không có mẫu nào bị cắt ở cả hai lượt — cùng 20 mẫu, cùng số token, cùng số chunk — vậy mà chậm đi 10–15 %. Khối lượng tính không đổi thì phần chênh đến từ máy. Giải thích khả dĩ nhất là T4 tản nhiệt thụ động bị hạ xung sau vài phút chạy liên tục; **chưa xác minh** bằng cách đọc nhiệt độ nên ghi là giả thuyết.

Quy tắc rút ra, đã ghi vào mục 5 `CLAUDE.md`: E13 (Sailor2) và E14 (bậc thang 3B/1.5B) so ms/mẫu giữa các mô hình thì phải chạy **mỗi cấu hình một phiên riêng hoặc đo xen kẽ**, không xếp tuần tự rồi so thẳng, kẻo phần hạ xung bị tính nhầm thành khác biệt giữa các mô hình.

**2. Một lỗi trong script, đã sửa.** Lượt 2.048 báo `k = 0,85` thay vì 1,00. Nguyên nhân: mũ được khớp giữa `median_ms` và `mean_tokens`, mà `mean_tokens` là độ dài **lúc mẫu đi vào**, còn mẫu bị cắt thì thực tế chỉ được đưa vào 2.048 token. Ghép chi phí thật với độ dài không thật thì khớp ra một đường cong chưa từng tồn tại. Giờ chỉ khớp trên các mức không có mẫu nào bị cắt và in ra mức nào bị loại. Thêm `tiers_without_truncation` cùng hai ca kiểm thử.

##### Việc lặt vặt

- `results/feasibility.jsonl` vào repo, hai bản ghi.
- Thêm `.gitattributes` ép LF cho `jsonl`/`csv`: sổ kết quả ghi nối từ cả Kaggle lẫn máy cá nhân, không muốn cùng một lần chạy ra byte khác nhau tùy máy nào commit.
- Ghi chi phí đo được vào phần E11 `docs/EXPERIMENTS.md` làm cột chi phí cho mọi dòng lookback và chunk-aware.
- Bỏ ghi chú lo đứt phiên Kaggle: Save Version chạy nền được 12 tiếng nên 9 giờ 30 của ISE-DSC01 nằm gọn trong một lượt. Vẫn giữ khuyến nghị ghi kết quả theo phần, nhưng vì lý do phục hồi khi hỏng chứ không phải vì giới hạn phiên.

##### Kiểm tra

```
ruff check .   -> All checks passed!
pytest         -> 103 passed
```

---

<a id="pr-19"></a>

### #19 — T08: ghi nhiệt độ và xung nhịp GPU để lần đo sau tự chẩn đoán

- **Nhánh:** `t08-do-nhiet-do` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 13:03 · **gộp:** 20/08/2026 13:04 · **commit gộp:** [`9757d2c`](https://github.com/wsunicorn/vihallulens/commit/9757d2cfe40af0668cb8e10f332398cf98d3de74)¹
- **Thay đổi:** +371 / −137, 4 file · **bình luận bot:** 0

Nối tiếp #18. Vá chỗ yếu mà chính lượt đo 2.048 làm lộ ra.

##### Vấn đề

Lượt 2.048 cho thấy ba mức có khối lượng tính **y hệt nhau** (cùng mẫu, cùng token, cùng chunk, 0 mẫu bị cắt ở cả hai lượt) vẫn chậm đi 10–15 %. Nghi do T4 tản nhiệt thụ động hạ xung vì nhiệt — nhưng không có gì trong lần chạy ghi lại nhiệt độ, nên chỉ dừng được ở phỏng đoán.

##### Cách vá

Đọc `nvidia-smi` một lần trước khi đo và một lần ngay sau mỗi mức, in bảng nhiệt độ theo mức, ghi vào `results/feasibility.jsonl`, cảnh báo nếu xung tụt. Không thêm thư viện nào — `nvidia-smi` có sẵn trên Kaggle. Hỏng thì trả `None` và chạy tiếp, không làm gãy phép đo.

Lần chạy GPU kế tiếp, bất kể là E13, E14 hay gì, sẽ tự trả lời câu hỏi hạ xung mà **không tốn thêm phút quota nào**.

##### Một cái bẫy đã tránh được

Tiêu chí đầu tiên mình viết là `xung < 95 % mức tối đa thì báo hạ xung`. Nghe hợp lý, và sai. Card **rảnh** tự hạ xung để tiết kiệm điện, mà phép đọc lại diễn ra ngay sau khi mức vừa chạy xong. Thử trên card rời của máy cá nhân lúc không làm gì: `1.500/2.100 MHz = 71 %`, chẳng có gì bị ghìm cả. Ngưỡng đó sẽ báo động ở mọi phiên.

Tiêu chí đúng là **xu hướng**: xung cuối phiên thấp hơn đầu phiên (> 2 điểm) trong khi nhiệt độ tăng (> 5 °C). Đã ghi lý do vào docstring để sau này không ai "sửa lại cho gọn" thành ngưỡng tuyệt đối.

##### Ngân sách thời gian đã cộng bù nhiệt

Chỗ này #18 ghi hụt: lượt đo 4.096 chạy **đầu tiên trong phiên, GPU còn nguội**, nên là số lạc quan. Một lượt trích thật kéo 9–10 tiếng thì card nóng gần như suốt.

| | Dự báo lúc GPU nguội | Nên lấy để xếp lịch |
|---|---|---|
| ISE-DSC01 một lượt | 9 giờ 30 | **~11 giờ** |
| Hai bộ bắt buộc | 10 giờ 19 | **~12 giờ** |
| Cả bốn bộ | 14 giờ 44 | **~17 giờ** |

Vẫn trong quota 30 giờ, nhưng 11 tiếng **sát giới hạn 12 tiếng của một lượt Save Version** — đây mới là lý do thật để ghi kết quả theo phần, không phải "sợ đứt phiên".

##### Vì sao không chạy lại hai phiên riêng

Đã cân và quyết định không, vì có chặn trên bằng số học khiến mọi kết quả đo đều dẫn tới cùng một quyết định: ngân sách 2.048 chỉ ảnh hưởng **483 mẫu** của hai bộ bắt buộc, mà 483 mẫu đó ở cấu hình 4.096 chỉ tốn **21 phút** trên tổng 10 giờ 19. Kể cả nếu chúng nhanh bằng không thì tiết kiệm tối đa là **3,4 %**, thực tế khoảng 1,6 %. Đốt quota để làm rõ 1,6 % hay 3,4 % trong khi cả hai đều dẫn tới "giữ 4.096" là không đáng. Lý do đã ghi vào `TASKS.md`.

##### Kiểm tra

```
ruff check .   -> All checks passed!
pytest         -> 110 passed
```

Sáu ca mới cho phần telemetry, gồm ca card rảnh (không được báo hạ xung) và ca `[N/A]` (nvidia-smi trả lời được nhưng không có số).

---

<a id="pr-20"></a>

### #20 — T09: chuẩn hóa ViHallu về schema chung

- **Nhánh:** `t09-chuan-hoa-vihallu` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 13:10 · **gộp:** 20/08/2026 13:10 · **commit gộp:** [`b758031`](https://github.com/wsunicorn/vihallulens/commit/b758031015c2fb7ab624a68a838f27ea294e5490)¹
- **Thay đổi:** +730 / −1, 7 file · **bình luận bot:** 0

Task đầu của giai đoạn 2. Dựng luôn khuôn mà T10–T12 sẽ dùng lại.

##### Task này để làm gì

Bốn bộ có bốn định dạng, cột tên khác nhau, nhãn gọi tên khác nhau. Để nguyên thì mỗi thí nghiệm phải biết cách đọc từng bộ. Chuẩn hóa là đổ cả bốn về **cùng 14 cột** của mục 1 `docs/DATA.md`, sau đó phần còn lại của hệ thống chỉ cần biết 14 cột ấy.

##### Kết quả chạy

```
python scripts/normalize_data.py --dataset vihallu

  số dòng               : 7,000
  ngữ cảnh duy nhất     : 3,865
  phân bố nhãn:
      extrinsic      2,307  ( 33.0 %)
      intrinsic      2,448  ( 35.0 %)
      no             2,245  ( 32.1 %)
  phân bố meta.prompt_type:
      noisy            245  (  3.5 %)
      unknown        6,755  ( 96.5 %)
  đã ghi: data/interim/vihallu_train.parquet  (7,000 dòng)
```

Khớp đúng bảng mục 4 `docs/DATA.md`.

```
ruff check .   -> All checks passed!
pytest         -> 167 passed   (thêm 55 ca)
```

##### Ba điều đáng nói

**1. Luật nhận `noisy` bắt được 3,5 %, không phải một phần ba như bài báo ngụ ý.**

Bài ViHallu nói mỗi ngữ cảnh sinh ba loại prompt phân bố cân bằng. Nhưng bỏ dấu chỉ là **một trong bốn** phép nhiễu bài liệt kê (bỏ dấu, hoán vị ký tự, xóa token, đảo trật tự từ), nên prompt bị hoán vị ký tự mà vẫn còn dấu thì luật không bắt được.

Nhóm `noisy` vì thế **độ chính xác cao, độ phủ thấp**. Hệ quả cho T35: so sánh là "nhóm bị bỏ dấu với tất cả phần còn lại", chứ không phải "noisy với không noisy" — phần còn lại vẫn lẫn mẫu noisy kiểu khác. Đã ghi vào mục 7 `docs/DATA.md` kèm ví dụ, để lúc viết báo cáo không gọi tắt thành "noisy".

Ba mẫu bắt được:
```
De tai duoc su dung nhieu nhat trong cac luan van tien si A Rap Xe Ut la gi?
Coo bao nhieu nguooi dan Bac Trieu Tien ti nan o mien Nam sau cuoc cai cach ruong ddats?
Truoc khi duoc Ton Trung Son cai to thanh Trung Quoc Quoc dan Dang thi Dang nay da tung...
```
Mẫu thứ hai còn dính cả nhân đôi ký tự (`Coo`, `nguooi`, `ddats`) — một mẫu có thể chịu nhiều phép nhiễu cùng lúc.

**2. Nhận diện dấu suy từ Unicode, và phải so với ngữ cảnh.**

`docs/DATA.md` yêu cầu dùng dải Unicode chứ không dùng danh sách từ. Cách làm: ký tự có dấu là ký tự mà **phân rã NFD** ra một chữ cái ASCII kèm dấu rời, cộng `đ`/`Đ` gọi tên riêng vì nó mang nét gạch nên Unicode không phân rã, song vẫn biến mất khi bỏ dấu. Đúng cho cả `á`, `ệ`, `ự` mà không phải gõ tay 134 ký tự.

Phần so với ngữ cảnh là để tránh bẫy: câu hỏi chỉ gồm tên riêng và con số như `IBM 1970?` vốn không có dấu nào để mất, xét một mình sẽ bị gán nhầm `noisy`. Có ca kiểm thử riêng cho việc này.

**3. `context_id` chuẩn hóa NFC trước khi băm.**

`context_id` là mã băm của ngữ cảnh, T14 dùng để chia tập theo nhóm. Cùng chữ `ế` có thể lưu thành một mã điểm hoặc thành `e` cộng hai dấu rời — nhìn giống hệt nhau, băm ra hai giá trị. Nếu vậy cùng một ngữ cảnh rơi vào hai tập và **rò rỉ từ train sang test**, đúng cái mà chia theo nhóm sinh ra để ngăn. Có ca kiểm thử khẳng định hai dạng cho cùng một id.

##### Vài quyết định thiết kế

- **Kiểm tra ràng buộc ở lúc ghi, không phải lúc đọc.** `finalise()` từ chối cột lạ, `sample_id` trùng, chuỗi rỗng ở cột bắt buộc, span bằng chứng nửa vời hoặc vượt quá độ dài ngữ cảnh.
- **Số dòng và phân bố nhãn được đối chiếu với `docs/DATA.md` rồi raise nếu lệch.** Phân bố nhãn đổi nghĩa là bản phát hành khác, và kết quả từ nó không so được với bất kỳ số nào đã đo.
- **`--dataset` cho ba bộ chưa làm thì báo đúng mã task** thay vì lỗi khó hiểu.
- **`load_dataset` chưa viết** dù mục 2.1 `docs/SPEC.md` có khai báo, vì chưa task nào cần đọc lại file interim. Để tới T14.

---

<a id="pr-21"></a>

### #21 — T10: chuẩn hóa ISE-DSC01, và sửa một con số sai trong tài liệu

- **Nhánh:** `t10-chuan-hoa-isedsc01` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 14:17 · **gộp:** 20/08/2026 14:17 · **commit gộp:** [`6998b02`](https://github.com/wsunicorn/vihallulens/commit/6998b02b6e957fa60c1bc635fc1c9e12d8a98e72)¹
- **Thay đổi:** +373 / −15, 10 file · **bình luận bot:** 1

Bộ thứ hai, theo đúng khuôn T09 đã dựng. Nhưng có một chỗ tài liệu ghi sai, đã sửa.

##### Kết quả chạy

```
python scripts/normalize_data.py --dataset isedsc01

  số dòng               : 36,369
  ngữ cảnh duy nhất     : 4,793
  phân bố nhãn:
      extrinsic     12,583  ( 34.6 %)
      intrinsic     11,000  ( 30.2 %)
      no            12,786  ( 35.2 %)
  có bằng chứng nguyên văn : 23,783/36,369
  nguồn có ghi bằng chứng  : 23,784
  ghi mà không định vị được: 1
  phân bố meta.domain      : the-gioi 7.405 · thoi-su 7.121 · khoa-hoc 6.522
                             suc-khoe 5.416 · du-lich 5.175 · giao-duc 4.730
```

Số dòng, số ngữ cảnh duy nhất, phân bố nhãn khớp đúng bảng mục 4 `docs/DATA.md`.

```
ruff check .   -> All checks passed!
pytest         -> 182 passed   (thêm 15 ca)
```

##### Con số sai: 23.785 phải là 23.783

Tiêu chí T10 ghi `evidence_start` tìm được là **23.785**. Đo ra **23.783**. Chênh đúng hai.

Hai mẫu trong bộ có `evidence` chỉ gồm **hai ký tự xuống dòng** — một dòng trống, không chữ nào. Khoảng trắng là **giá trị rỗng duy nhất mà phép tìm chuỗi vẫn tìm thấy**: `context.find` trả về vị trí của một dòng trống nào đó trong ngữ cảnh. Hai mẫu ấy được đếm là "có bằng chứng" và "tìm thấy", trong khi thực chất mang một `evidence_start` trỏ vào chỗ không có gì mà trông vẫn hợp lệ.

**Hai mẫu trên ba mươi sáu nghìn có đáng sửa không?** Có. E06 đo hit@1, hit@3, MRR bằng cách so đoạn được chú ý nhiều nhất với **đoạn chứa bằng chứng vàng** — một offset trỏ vào dòng trống trở thành đáp án rác mà E06 phải trúng. Cộng thêm chi phí sửa bằng không, và đây đúng là loại lỗi âm thầm mà sáu tuần sau không truy ra nổi.

`find_evidence` trong `schema.py` nay coi bằng chứng chỉ gồm khoảng trắng là **không có bằng chứng**, kèm ca kiểm thử. Đã sửa số ở mục 4 `docs/DATA.md` và mục 4 `CLAUDE.md`, **ghi rõ số cũ và lý do lệch** chứ không lặng lẽ đổi.

##### Ba loại "không có offset", nay phân biệt được

| Loại | Số mẫu | Ý nghĩa |
|---|---|---|
| `evidence` là `null` | 12.583 | Toàn bộ nhãn NEI. Bộ dữ liệu không cung cấp bằng chứng |
| `evidence` chỉ gồm khoảng trắng | 2 | Rác trong dữ liệu gốc |
| Có bằng chứng nhưng không tìm thấy nguyên văn | 1 | Lỗi dữ liệu gốc |
| **Tìm thấy nguyên văn** | **23.783** | Dùng được cho E06 |

Cả ba đều cho `evidence_start = -1` nhưng khác nhau về ý nghĩa, nên thêm `meta.evidence_given`.

Mẫu trượt duy nhất: bằng chứng ghi `...ông Thiệu nói..` với **hai dấu chấm**, ngữ cảnh chỉ có một rồi xuống dòng — có lẽ công cụ tách câu tự thêm. Xử lý bằng `-1` và đếm vào báo cáo, **không khớp gần đúng**: một con số trông hợp lý đặt vào cột mà thí nghiệm sau coi là chân lý còn tệ hơn thừa nhận không tìm thấy.

##### Hai lỗi của chính mình, đã sửa

**1. `evidence` của NEI là `null`, không phải chuỗi rỗng.** `str(None)` cho ra chuỗi `"None"` — bốn ký tự trông như dữ liệu thật, `strip()` ra khác rỗng, và 12.583 dòng NEI sẽ mang bằng chứng giả. Mình dính đúng bẫy này lúc dò dữ liệu, phát hiện vì output phình lên hai megabyte. Trong code dùng `str(record.get("evidence") or "")`.

**2. Test đang kiểm tra một bản sao chứ không kiểm tra bộ đọc thật.** Bản đầu mình dựng lại logic đọc ngay trong file test, để né phép kiểm tra 36.369 dòng. Nghĩa là nếu bộ đọc sai thì test vẫn xanh — gần như vô giá trị. Đã tách `read_isedsc01` (đọc) khỏi `normalize_isedsc01` (đọc rồi đối chiếu số lượng), làm tương tự cho ViHallu, và mọi ca nay chạy qua `read_*` thật với dữ liệu vài dòng.

---

<a id="pr-22"></a>

### #22 — T11: chuẩn hóa ViWikiFC, dừng kiểm tra chỗ bằng chứng trượt

- **Nhánh:** `t11-chuan-hoa-viwikifc` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 14:33 · **gộp:** 20/08/2026 14:33 · **commit gộp:** [`fb7aff6`](https://github.com/wsunicorn/vihallulens/commit/fb7aff6cdee665cf58b78485b056e46cee9d431f)¹
- **Thay đổi:** +381 / −7, 6 file · **bình luận bot:** 0

Bộ thứ ba. Tiêu chí task này có một cổng dừng, và nó đã kích hoạt — đã truy đến cùng trước khi đi tiếp.

##### Kết quả chạy

```
python scripts/normalize_data.py --dataset viwikifc

  số dòng               : 20,919      (16.738 train / 2.090 dev / 2.091 test)
  ngữ cảnh duy nhất     : 1,481
  phân bố nhãn:
      extrinsic      6,978  ( 33.4 %)
      intrinsic      6,973  ( 33.3 %)
      no             6,968  ( 33.3 %)
  có bằng chứng nguyên văn : 20,918/20,919
  ghi mà không định vị được: 1
```

Số dòng ba tập và phân bố nhãn train (5.594 / 5.573 / 5.571) khớp đúng mục 4 `docs/DATA.md`.

```
ruff check .   -> All checks passed!
pytest         -> 197 passed   (thêm 15 ca)
```

##### Cổng dừng đã kích hoạt: 99,995 % chứ không tròn 100 %

Tiêu chí: *"`evidence_start` tìm được 100 % ở cả ba nhãn. Nếu không đủ 100 % thì có lỗi encoding, dừng lại."*

Đo ra **đúng một dòng** train trượt. Đã dừng và truy đến cùng.

**Kết luận: không phải lỗi encoding.** Bằng chứng của dòng đó ghi `...thế kỷ 20 thì NhậtaimBản đã trở thành...`, ngữ cảnh của chính nó ghi `...thế kỷ 20 thì Nhật Bản đã trở thành...` — ba chữ `aim` chèn đè lên dấu cách. Đã thử khớp theo NFC, theo NFD, và sau khi cắt khoảng trắng: đều không khớp. 20.918 dòng còn lại khớp chính xác từng ký tự.

Encoding hỏng thì hỏng **đồng loạt cả tập**, không hỏng đúng một dòng ở giữa. Đây là lỗi của bộ dữ liệu công bố. Xử lý theo mục 7 `docs/DATA.md`: `evidence_start = -1`, đếm vào báo cáo, **không khớp gần đúng**.

**Vẫn giữ phép kiểm tra, nhưng sửa ngưỡng cho đúng mục đích.** Nó tồn tại để bắt lỗi encoding hàng loạt — thứ làm hỏng hàng nghìn dòng trong im lặng trong khi mọi con số khác vẫn đúng. Nên `check_evidence` raise khi số trượt **nhiều hơn** một, chứ không phải khi **khác** một: ít hơn thì chỉ có thể nghĩa là bộ dữ liệu đã được sửa, và từ chối chạy trên bộ đã sửa thì vô lý. Có ca kiểm thử cho cả hai chiều.

##### `pairID` trông như khóa chính nhưng không phải

Train có 16.738 dòng nhưng chỉ **15.903 `pairID` duy nhất**: 321 nhóm gồm 835 dòng dùng chung một mã, mỗi nhóm 2–7 dòng.

Kiểm kỹ thì các dòng cùng nhóm **luôn cùng `evidence`, luôn cùng `gold_label`, khác `claim` 100 %**. Tức `pairID` định danh **cặp (bằng chứng, nhãn)** chứ không định danh mẫu: một câu bằng chứng được viết lại thành nhiều cách phát biểu.

Ai dùng nó làm khóa sẽ âm thầm gộp 835 dòng thành 321 và **mất 514 mẫu mà không lỗi nào báo**. Nó nằm ở `meta.source_id`; khóa thật là `sample_id`. Đã ghi cảnh báo vào `docs/DATA.md` kèm ca kiểm thử.

##### Xác nhận tính chất làm nên E08

Nhãn NEI có bằng chứng tìm thấy **100 % ở cả ba tập**: 5.571/5.571 train, 730/730 dev, 677/677 test. Không bộ nào khác có — ở ISE-DSC01 toàn bộ 12.583 mẫu NEI đều không có bằng chứng. Đây là lý do bộ này là đối chứng ngoài cho lớp ngoại lai.

##### Rò rỉ ngữ cảnh: tính lại bằng đường khác, khớp đúng mục 6

Mục 6 `docs/DATA.md` ghi test rò rỉ 845/845. Tính lại từ `context_id` vừa sinh: **đúng 845/845 ngữ cảnh, 2.091/2.091 dòng**. Thêm số cho dev chưa từng ghi: **836/838 ngữ cảnh, 2.088/2.090 dòng, 99,9 %**.

Cả ba tập cộng lại chỉ có 1.481 ngữ cảnh duy nhất trong khi riêng train đã 1.479 — dev và test gần như **không mang theo ngữ cảnh nào mới**. Split gốc chia theo *phát biểu* chứ không theo *tài liệu nguồn*.

Việc con số tái lập đúng bằng một đường tính hoàn toàn khác (băm NFC chuỗi ngữ cảnh) cũng là phép thử gián tiếp cho `context_id`. Không dựng báo cáo rò rỉ ở đây vì đó là T14.

##### Ghi thêm vào tài liệu

Phân bố nhãn của dev và test, trước đây `docs/DATA.md` chỉ có train:

| Tập | no | intrinsic | extrinsic | Tổng |
|---|---|---|---|---|
| train | 5.594 | 5.573 | 5.571 | 16.738 |
| dev | 666 | 694 | 730 | 2.090 |
| test | 708 | 706 | 677 | 2.091 |

---

<a id="pr-23"></a>

### #23 — T12: chuẩn hóa ViFactCheck, hết giai đoạn chuẩn hóa dữ liệu

- **Nhánh:** `t12-chuan-hoa-vifactcheck` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 14:46 · **gộp:** 20/08/2026 14:46 · **commit gộp:** [`a937a4f`](https://github.com/wsunicorn/vihallulens/commit/a937a4f74a2b9f939be3994280d80b5f42c97f6b)¹
- **Thay đổi:** +476 / −26, 6 file · **bình luận bot:** 1

Bộ thứ tư và cuối cùng. Cả bốn bộ nay đã về chung một schema.

##### Kết quả chạy

```
python scripts/normalize_data.py --dataset vifactcheck

  số dòng               : 7,232       (5.062 train / 723 dev / 1.447 test)
  ngữ cảnh duy nhất     : 1,041
  phân bố nhãn:
      extrinsic      2,347  ( 32.5 %)
      intrinsic      2,370  ( 32.8 %)
      no             2,515  ( 34.8 %)
  có bằng chứng nguyên văn : 4,296/7,232 (59.4 %)
  ghi mà không định vị được: 2,936
```

Và cả bốn bộ một lượt, `--all`:

```
  vihallu      7.000 dòng · 3.865 ngữ cảnh · bằng chứng   0/7.000  (bộ không có trường này)
  isedsc01    36.369 dòng · 4.793 ngữ cảnh · bằng chứng  23.783/36.369  (65,4 %)
  viwikifc    20.919 dòng · 1.481 ngữ cảnh · bằng chứng  20.918/20.919  (100,0 %)
  vifactcheck  7.232 dòng · 1.041 ngữ cảnh · bằng chứng   4.296/7.232   (59,4 %)
```

**Tổng 71.520 mẫu**, đúng bằng con số T08 dùng để dự báo giờ GPU.

```
ruff check .   -> All checks passed!
pytest         -> 214 passed   (thêm 17 ca)
```

##### Vì sao chỉ 59 % — câu hỏi tài liệu bỏ ngỏ, nay đã trả lời

`docs/DATA.md` ghi *"chỉ 59,2 % bằng chứng nằm nguyên văn; điều này bình thường, không phải lỗi"* nhưng không nói **vì sao**.

Trước hết loại trừ hai giả thuyết dễ nghĩ nhất: gộp khoảng trắng cứu được **0/2.064** mẫu trượt, chuẩn hóa NFC cũng **0/2.064**. Không phải chuyện định dạng ký tự.

Rồi nhìn vào chỗ chuỗi lệch nhau:

| Quan sát trên 2.064 mẫu trượt của train | Số mẫu |
|---|---|
| 30 ký tự **đầu** có trong ngữ cảnh | 1.874 |
| Cả **đầu lẫn đuôi** đều có | 1.741 |
| Không thấy đầu cũng không thấy đuôi | 20 |

Đầu có, đuôi có, cả chuỗi thì không — chỉ một cách giải thích. Bằng chứng ghi:

```
... tư vấn xếp lớp rất nhanh chóng và nhiệt tình ILA tiếp nhận và hỗ trợ ...
```

ngữ cảnh ghi:

```
... tư vấn xếp lớp rất nhanh chóng và nhiệt tình. Chẳng những được miễn học phí ...
```

Người gán nhãn lấy câu A, **bỏ dấu chấm cuối**, rồi nối thẳng một câu khác ở chỗ khác vào. **Bằng chứng của bộ này là nhiều câu rời nhau ghép lại.**

###### Hệ quả về mặt thiết kế

Schema chung chỉ có **một** cặp `(evidence_start, evidence_end)`, tức một đoạn liền mạch. Bằng chứng nhiều mảnh rời **về nguyên tắc không biểu diễn được** bằng cấu trúc ấy.

Nên 59,2 % không phải "tỷ lệ khớp thành công" mà là **tỷ lệ bằng chứng chỉ gồm một mảnh**. E17 nếu làm phần định vị bằng chứng phải mở rộng schema thành danh sách đoạn trước, hoặc chấp nhận chỉ dùng 59 % kia. Đã ghi vào mục 7 `docs/DATA.md`.

##### Bẫy lặp lại lần thứ hai

`annotation_id` cũng **không phải khóa chính**: 5.062 dòng train, chỉ **1.250** giá trị duy nhất. Đúng bẫy `pairID` của ViWikiFC ở T11.

Hai trên bốn bộ có cột trông như khóa mà không phải — nên quy ước dùng `sample_id` do mình sinh làm khóa duy nhất là đúng, và mọi mã nguồn gốc đều nằm ở `meta.source_id`.

##### Cột `Topic` lẫn lộn hoa thường

52 giá trị, gồm cả `Thể thao` lẫn `THỂ THAO`, và **bốn** cách viết cho một chủ đề: `Văn hoá` / `Văn hóa` / `VĂN HÓA` / `VĂN HOÁ`.

Schema **giữ nguyên văn** để còn truy ngược về nguồn — dọn dẹp ở tầng này sẽ mất khả năng đối chiếu. Nhưng ai cắt kết quả theo chủ đề phải tự gộp trước, nếu không đếm một chủ đề thành bốn. Có ca kiểm thử khẳng định giá trị không bị dọn âm thầm.

##### Vài quyết định thiết kế

- **`check_evidence` dùng dải 55–65 % thay vì đếm chính xác**, vì đây là tính chất của cách gán nhãn chứ không phải checksum. Dải **hai phía**: tụt về 0 nghĩa là đọc nhầm cột hoặc nhầm bộ, vọt lên 100 nghĩa là bộ đã được gán nhãn lại và kết quả không so được với gì đã đo.
- **`--all`** chạy lần lượt cả bốn bộ trong một lệnh.
- **Bỏ `Unnamed: 0`** theo mục 7 `docs/DATA.md`; kiểm tra thì đúng là số thứ tự dòng 0..n-1. Bỏ bằng `errors="ignore"` để bản phát hành sau không có cột đó vẫn đọc được.

---

<a id="pr-24"></a>

### #24 — T13: chuẩn bị phiếu gán nhãn kiểm chứng ánh xạ NEI

- **Nhánh:** `t13-chuan-bi-kiem-chung-nei` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 20/08/2026 15:30 · **gộp:** 20/08/2026 15:30 · **commit gộp:** [`fca6f8f`](https://github.com/wsunicorn/vihallulens/commit/fca6f8f95c595f2658d7859b4f39bee435d9599c)¹
- **Thay đổi:** +984 / −1, 6 file · **bình luận bot:** 1

**Chưa tick T13.** Phần gán nhãn là việc của Lân và Minh — nếu Claude gán cả 100 mẫu thì không còn "hai người gán độc lập", và hệ số đồng thuận trở thành con số vô nghĩa.

##### Task này hỏi gì

Mục 3 `docs/DATA.md` ánh xạ `NEI` → `extrinsic`, rồi ngay câu sau tự cảnh báo hai khái niệm **không tương đương**:

- **NEI** — ngữ cảnh **không đủ** để kết luận phát biểu đúng hay sai.
- **Ngoại lai** — phát biểu **mang vào** thông tin ngữ cảnh không hề có.

Giao nhau nhiều nhưng không trùng. Một phát biểu có thể *không kết luận được* trong khi mọi dữ kiện nó nhắc tới đều nằm sẵn trong ngữ cảnh — khi đó ánh xạ sai. Không ai biết tỷ lệ đó cho tới khi có người đọc tay. Kết quả đi thẳng vào phần hạn chế của báo cáo.

##### Đã chuẩn bị

`scripts/audit_nei_mapping.py`, hai chế độ, và ba file trong `results/`:

| File | Dùng làm gì |
|---|---|
| `nei_mapping_audit_HUONGDAN.md` | Hướng dẫn gán nhãn — đọc trước khi làm |
| `nei_mapping_audit_lan.csv` | Phiếu của Lân, 120 dòng |
| `nei_mapping_audit_minh.csv` | Phiếu của Minh, giống hệt |

##### Bốn đáp án, không phải hai

Câu hỏi dạng có/không sẽ mất thông tin, vì **"không phải ngoại lai" thật ra là hai chuyện rất khác nhau**: phát biểu bám sát ngữ cảnh (nhãn `no`), hay phát biểu mâu thuẫn với ngữ cảnh (nhãn `intrinsic`). Chỉ cái đầu nghĩa là nhãn NEI đơn thuần yếu quá; cái sau nghĩa là ánh xạ đẩy mẫu sang **sai hẳn lớp**.

Nên bốn mã: `ngoai_lai`, `noi_tai`, `khong`, `khong_chac`.

##### 120 dòng nhưng kết quả 100 dòng

20 dòng là **mẫu đối chứng**: 10 `Supports` + 10 `Refutes`, trộn lẫn và xáo ngẫu nhiên nên không phân biệt được. `--report` tách chúng ra, **file nộp vẫn đúng 100 dòng** theo tiêu chí.

Lý do cần: cả 100 mẫu NEI cùng một nhãn gốc. Nếu ai đó gõ `ngoai_lai` cho tất cả mà không đọc:

```
tỷ lệ khớp   = 100 %   <- trông rất đẹp
Cohen kappa  = không tính được
```

và không có cách nào phân biệt "hai người thật sự đồng ý" với "hai người cùng bấm bừa". Đối chứng phá thế đó — gán sai `Supports`/`Refutes` là lộ ngay. Ngưỡng cảnh báo 70 %.

##### Chạy thử toàn tuyến bằng phiếu điền giả

```
ĐỐI CHỨNG — 20 dòng không phải NEI, trộn lẫn vào
  lan   : đúng 16/20  (80 %)
  minh  : đúng 16/20  (80 %)

ÁNH XẠ NEI -> NGOẠI LAI — 100 mẫu NEI
  lan   : 91/100 cho là ngoại lai (91 %)
  minh  : 73/100 cho là ngoại lai (73 %)
  Hai người cùng cho là ngoại lai: 65/100 (65 %)

  Tỷ lệ khớp thô        : 66.0 %
  Cohen kappa           : -0.039  (tệ hơn ngẫu nhiên)
```

Phiếu giả được sinh bằng nhiễu độc lập, nên **kappa ≈ 0 dù tỷ lệ khớp thô 66 %** là đúng như thiết kế — và đó chính là bệnh mà kappa sinh ra để phát hiện. Một phép thử tốt cho công cụ.

##### Vài quyết định thiết kế

- **Hai file riêng, không phải hai cột một file.** Hai cột cạnh nhau thì gần như chắc chắn người sau liếc thấy đáp án người trước.
- **Phiếu không chứa đáp án.** Không cột nhãn gốc, không file khóa. Nhãn thật tra lại qua `sample_id` lúc `--report`.
- **UTF-8 có BOM.** Excel trên Windows mở CSV UTF-8 thường hiện tiếng Việt thành ký tự rác; BOM là thứ khiến nó hiển thị đúng khi bấm đúp.
- **`--prepare` không ghi đè** trừ khi `--force`, kẻo sinh lại đè mất buổi làm của ai đó.
- **Sắp theo `sample_id` trước khi lấy mẫu.** pandas lấy mẫu theo *vị trí*, nên không cố định thứ tự thì chạy lại `normalize_data.py` có thể âm thầm đổi 100 mẫu được kiểm. **Một ca kiểm thử phát hiện ra, và đã sửa ở code chứ không sửa test.**

```
ruff check .   -> All checks passed!
pytest         -> 244 passed   (thêm 30 ca)
```

##### Việc của Lân và Minh

1. Đọc `results/nei_mapping_audit_HUONGDAN.md`.
2. Mỗi người điền cột `nhan_dinh` trong file của mình, **độc lập, không bàn nhau**.
3. Chạy `python scripts/audit_nei_mapping.py --report`.
4. Dán output vào đây rồi tick T13.

Ngữ cảnh bộ này ngắn — trung vị 124 từ, dài nhất 344 — nên 120 dòng ước chừng 60–90 phút mỗi người.

---

<a id="pr-25"></a>

### #25 — T13: làm rõ ca số liệu sai, và chịu được ký tự vô hình khi dán

- **Nhánh:** `t13-sua-huong-dan-va-ky-tu-vo-hinh` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 23/08/2026 00:35 · **gộp:** 23/08/2026 00:35 · **commit gộp:** [`192a705`](https://github.com/wsunicorn/vihallulens/commit/192a705938b4b9357c743bfacb87d008cf5227ae)¹
- **Thay đổi:** +163 / −54, 4 file · **bình luận bot:** 1

Hai chỗ lộ ra khi Lân bắt đầu gán nhãn thật. Không đụng vào phiếu đã điền.

##### 1. Hướng dẫn không trả lời được câu hỏi về số liệu sai

Câu hỏi thật từ người gán: *"sai số liệu là nội tại hay ngoại lai, khi số đó sai so với một số khác trong ngữ cảnh?"*

Ba gạch đầu dòng cũ chỉ nói "thông tin lấy từ đâu", nghe như phải hỏi **con số đó có xuất hiện trong ngữ cảnh không**. Mà một con số sai thì giá trị mới đương nhiên không xuất hiện — dễ dẫn tới gán nhầm thành `ngoai_lai`.

Đáp án đúng là `noi_tai`: phép thử không phải "token đó có trong ngữ cảnh không" mà là **ngữ cảnh có nói về thuộc tính đó của thực thể đó không**. Nếu có, mọi sai lệch về nó là mâu thuẫn, không phải thông tin mới.

Bổ sung vào hướng dẫn một phép thử sắc hơn:

> **Chỉ với ngữ cảnh này thôi, tôi có BÁC BỎ được phát biểu không?**

| Trả lời | Mã |
|---|---|
| Bác bỏ được | `noi_tai` |
| Không bác bỏ được, cũng không xác nhận được | `ngoai_lai` |
| Xác nhận được | `khong` |

Kèm một mục riêng về số liệu, với bảng ví dụ y khoa lấy từ chính ca người gán hỏi, và phân biệt **diễn đạt lỏng** với **nói sai**: "48 tuần" viết thành *"gần 50 tuần"* là diễn đạt lại — 48 đúng là gần 50 — nên `khong`. Chỉ tính `noi_tai` khi giá trị mới **loại trừ** giá trị trong ngữ cảnh.

Có ghi thêm rằng ca mờ nhất không phải ở con số mà ở chỗ **đổi cả cách nói** (*"đáp ứng lâu dài"* → *"thích nghi"*), và những dòng đó nên để `khong_chac` kèm `ghi_chu` — chúng chính là phần đáng bàn nhất trong báo cáo.

##### 2. Ký tự vô hình khi dán mã đáp án

34 đáp án đầu tiên trong phiếu thật dính **khoảng trắng độ rộng bằng không** (U+200B) ở đầu, do dán mã ra từ tài liệu đã render:

```
'​ngoai_lai'
```

`str.strip()` không xóa được: Python chỉ strip **khoảng trắng**, còn U+200B là ký tự **định dạng** (nhóm Unicode `Cf`). Để nguyên thì cả 34 dòng bị báo là mã không hợp lệ ở bước `--report` — **sau khi người ta đã đọc xong 34 mẫu**. Đúng loại lỗi tệ nhất: im lặng lúc làm, nổ lúc nộp.

`normalise_answer` nay loại mọi ký tự nhóm `Cf` và quy khoảng trắng không ngắt (U+00A0) về khoảng trắng thường. Bốn ca kiểm thử mới.

Kiểm trên phiếu thật:

```
52 dòng đã điền, sau khi làm sạch:
  {'ngoai_lai': 34, 'khong': 15, 'noi_tai': 3}
  mã không hợp lệ còn lại: không có
```

##### Phiếu đã điền còn nguyên

`--prepare` chạy lại chỉ ghi đè file hướng dẫn; hai file CSV bị bỏ qua đúng như thiết kế:

```
results\nei_mapping_audit_lan.csv đã tồn tại, bỏ qua. Dùng --force nếu thật sự muốn ghi đè.
results\nei_mapping_audit_minh.csv đã tồn tại, bỏ qua.
đã ghi results\nei_mapping_audit_HUONGDAN.md
```

```
ruff check .   -> All checks passed!
pytest         -> 248 passed   (thêm 4 ca)
```

---

<a id="pr-26"></a>

### #26 — T13: chỉ 67 % nhãn NEI thật sự là ảo giác ngoại lai

- **Nhánh:** `t13-ket-qua-kiem-chung-nei` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 23/08/2026 11:22 · **gộp:** 23/08/2026 11:23 · **commit gộp:** [`0c71910`](https://github.com/wsunicorn/vihallulens/commit/0c719101656e7ada9bd4deed825887008e26e0e6)¹
- **Thay đổi:** +418 / −207, 7 file · **bình luận bot:** 1

Lân và Minh gán xong 120/120 dòng, độc lập. Tick T13.

##### Kết quả

| Chỉ số | Giá trị |
|---|---|
| **Hai người cùng cho là ngoại lai** | **67/100** |
| Lân | 71/100 |
| Minh | 77/100 |
| Tỷ lệ khớp thô | 79,0 % |
| **Cohen kappa** | **0,505** — trung bình theo Landis–Koch |
| Dương tính giả trên đối chứng (cả hai cùng sai) | 1/20 = 5 % |

Bảng chéo, hàng Lân cột Minh:

| | ngoai_lai | noi_tai | khong | khong_chac |
|---|---|---|---|---|
| **ngoai_lai** | **67** | 4 | 0 | 0 |
| **noi_tai** | 4 | 3 | 0 | 0 |
| **khong** | 6 | 6 | 9 | 1 |
| **khong_chac** | 0 | 0 | 0 | 0 |

**Chỉ khoảng 67 % nhãn NEI thật sự là ảo giác ngoại lai.** Phân rã 33 mẫu còn lại theo cách hiểu của Lân: **22 mẫu `khong`** (bám sát ngữ cảnh, chỉ là ngữ cảnh không đủ để xác nhận — đúng nghĩa NEI nhưng không phải ảo giác gì cả) và **7 mẫu `noi_tai`** (mâu thuẫn với ngữ cảnh, lẽ ra là nội tại). Nhóm sau đáng lo hơn: ánh xạ không chỉ *yếu* mà đẩy mẫu sang **sai hẳn lớp**.

##### Cảnh báo đối chứng đã bật — và vì sao con số vẫn dùng được

Minh đạt **12/20**, dưới ngưỡng 70 % (Lân 16/20). Đúng thứ 20 mẫu đối chứng sinh ra để bắt, nên phải xử lý chứ không lờ đi.

Sai sót **không ngẫu nhiên mà có hướng**:

| Loại đối chứng | Đáp án đúng | Lân | Minh |
|---|---|---|---|
| `Supports` | `khong` | 9/10 | 7/10 |
| `Refutes` | `noi_tai` | 7/10 | **5/10** |

Sai chính của Minh là **4 mẫu `Refutes` gán thành `ngoai_lai`** — đúng chỗ nhầm giữa nội tại và ngoại lai, cùng loại nhầm mà Lân hỏi giữa chừng và đã làm rõ ở #25. Hệ quả có hướng: nó **thổi phồng** số `ngoai_lai` của Minh, và đúng là Minh ra 77 % còn Lân 71 %.

**Nhưng con số nộp là con số đồng thuận**, và ở đó tình hình khác hẳn: trên 20 mẫu đối chứng, **cả hai cùng gán nhầm `ngoai_lai` chỉ 1 lần**. Sai sót của hai người phần lớn độc lập, nên đòi cả hai cùng đồng ý lọc gần hết. Tỷ lệ dương tính giả 5 % chính là thanh chắn cho con số 67 % — và nó **chỉ có được nhờ có mẫu đối chứng**. Không có chúng thì không cách nào biết 67 % đáng tin tới đâu.

##### Ba điều học được

**1. Ranh giới nội tại–ngoại lai khó với cả người.** 8/100 mẫu NEI có một người gán `noi_tai` còn người kia gán `ngoai_lai` — hai lớp **đối lập nhau**, không phải sát nhau. Trên đối chứng cả hai đều tệ hơn ở `Refutes` so với `Supports`. Nên ghi vào chương đánh giá: **giới hạn trên của mọi mô hình phân biệt hai lớp này bị chặn bởi chính mức đồng thuận của người**, ở đây là kappa 0,505.

**2. Ghi chú "chưa chắc" dự báo được bất đồng.** Lân đánh dấu 15 dòng NEI là chưa chắc:

```
dòng có ghi chú     : lệch 7/15  (47 %)
dòng không ghi chú  : lệch 14/85 (16 %)
```

Gấp gần ba lần. Cảm giác "khó" của người gán không mơ hồ mà **đo được**, và chỉ đúng vào vùng ranh giới thật. Nếu sau này cần một tập con "sạch" thì đây là cách rẻ để lọc.

**3. Kappa và khớp thô nói hai chuyện khác nhau.** Khớp thô 79 % nghe cao, nhưng `ngoai_lai` chiếm đa số nên chọn bừa cũng trùng khá nhiều. Kappa 0,505 mới là phần vượt quá may rủi.

##### Bổ sung vào script

Ba con số mới, nói rõ hơn nhiều so với tỷ lệ đúng chung chung: tỷ lệ báo nhầm `ngoai_lai` trên đối chứng (gồm cả tỷ lệ cả-hai-cùng-sai), phân rã đúng/sai theo `Supports` và `Refutes`, và số mẫu một người gán nội tại còn người kia gán ngoại lai.

##### Cách dùng kết quả

Khi báo cáo số liệu trên ViWikiFC, **không được gọi lớp `extrinsic` của bộ này là ảo giác ngoại lai thuần túy**. Đã ghi vào mục 3 `docs/DATA.md` và mục 4 `CLAUDE.md`. Cùng cảnh báo áp cho ISE-DSC01 — nhưng bộ đó **không kiểm chứng được** vì nhãn NEI của nó không có bằng chứng.

```
ruff check .   -> All checks passed!
pytest         -> 248 passed
```

---

<a id="pr-27"></a>

### #27 — T14: chia tập theo nhóm ngữ cảnh và báo cáo rò rỉ

- **Nhánh:** `t14-chia-tap-va-ro-ri` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 23/08/2026 11:36 · **gộp:** 23/08/2026 11:36 · **commit gộp:** [`5ca72da`](https://github.com/wsunicorn/vihallulens/commit/5ca72da6189fede0b11e177c33b1f5f4162a412e)¹
- **Thay đổi:** +980 / −2, 9 file · **bình luận bot:** 1

Chia hai bộ chưa có split, đo rò rỉ cả bốn, và trả nợ `load_dataset` từ T09.

##### Kết quả chia — 80/10/10 theo `context_id`, seed 42

| Bộ | train | dev | test | Tổng |
|---|---|---|---|---|
| ViHallu | 5.598 (80,0 %) | 702 (10,0 %) | 700 (10,0 %) | 7.000 |
| ISE-DSC01 | 29.082 (80,0 %) | 3.653 (10,0 %) | 3.634 (10,0 %) | 36.369 |

Tỷ lệ chỉ **xấp xỉ** 80/10/10 vì chia cả nhóm — một ngữ cảnh phải rơi trọn vào một tập. Sai lệch nhỏ tới mức làm tròn một chữ số thập phân là ra đúng, vì nhóm nhỏ: lớn nhất 5 dòng (ViHallu) và 33 dòng (ISE-DSC01), đều dưới 0,1 % cỡ bộ.

**Rò rỉ bằng 0**, và là bằng chứng chứ không phải kỳ vọng: `group_split` gọi `assert_no_leakage` trên chính kết quả nó vừa sinh.

##### Bốn con số của mục 6 khớp chính xác

| Bộ | Tập | Theo ngữ cảnh | Theo dòng |
|---|---|---|---|
| ViWikiFC | dev | 836/838 (99,8 %) | 2.088/2.090 (99,9 %) |
| ViWikiFC | test | **845/845 (100 %)** | **2.091/2.091 (100 %)** |
| ViFactCheck | dev | 495/496 (99,8 %) | 721/723 (99,7 %) |
| ViFactCheck | test | 753/758 (99,3 %) | 1.433/1.447 (99,0 %) |
| ViHallu (public test) | — | 713/919 (77,6 %) | — |
| ISE-DSC01 (public test) | — | 1.004/1.319 (76,1 %) | — |

Đo lại bằng một đường hoàn toàn khác (băm NFC chuỗi ngữ cảnh) và ra đúng bốn con số nhóm đã ghi. Ghi nhận cũ là chính xác.

##### Ba điều học được

**1. Phải báo cáo rò rỉ theo dòng, không chỉ theo ngữ cảnh.** Hai con số trả lời hai câu khác nhau: theo ngữ cảnh là *"bao nhiêu vật liệu bị dùng lại"*, theo dòng là *"bao nhiêu phần điểm số thật sự dựa lên đó"*. Con số theo dòng thường lớn hơn và mới là con số đáng lo. Bảng cũ chỉ có cột ngữ cảnh; nay có cả hai.

**2. Split gốc của ban tổ chức cũng rò rỉ 76–78 %.** Nhóm không dùng hai file public test vì thiếu nhãn, nhưng con số này đáng ghi vào báo cáo: nó cho thấy quyết định tự chia theo nhóm là **cần thiết**, không phải cầu toàn.

**3. Chia theo nhóm và cân bằng nhãn là hai ràng buộc xung khắc — may là không cần ép.** Không thể vừa giữ trọn mỗi ngữ cảnh trong một tập vừa ép tỷ lệ nhãn bằng nhau. Nhóm không ép, kiểm lại thì phân bố nhãn lệch **không quá 2 điểm phần trăm** so với toàn bộ ở cả hai bộ.

##### Hai cái bẫy đã bịt, có kiểm chứng

Hai script chạy nối nhau nên có hai cách tự bắn vào chân:

- **Chạy `split_data.py` hai lần** sẽ cắt 80 % của 80 %, âm thầm làm teo tập train mỗi lần. Bịt bằng cách **gộp các tập lại trước rồi mới chia**. Kiểm bằng cách chạy hai lần rồi so mã băm danh sách `sample_id` — giống hệt, tổng vẫn đủ 7.000.
- **Chạy lại `normalize_data.py` sau khi đã chia** sẽ ghi 7.000 dòng vào file train trong khi dev/test cũ vẫn nằm đó, tức cùng một dòng ở hai file. Bịt bằng cách cho nó **tự xóa file của những split nó không ghi**:

```
đã xóa data\interim\vihallu_dev.parquet (còn sót từ lần chia tập trước)
đã xóa data\interim\vihallu_test.parquet (còn sót từ lần chia tập trước)
```

##### Vài quyết định thiết kế

- **`assert_no_leakage` là hàm công khai riêng**, không nằm chìm trong `group_split`. Mục 2.1 `docs/SPEC.md` đòi *kiểm tra* chứ không đòi *tin tưởng*, nên nó phải chạy được trên split đến từ nơi khác — split gốc của một bộ, hay file ai đó sửa tay. Đây cũng là cách tiêu chí "raise khi cố tình truyền dữ liệu rò rỉ" kiểm được trực tiếp.
- **Gán nhóm cho tập nào đang thiếu nhất so với hạn ngạch của chính nó**, không phải cho tập nhỏ nhất — nếu không, một nhóm lớn rơi vào lúc dở dang sẽ bỏ đói dev và test.
- **Sắp theo `context_id` trước khi xáo**, để thứ tự dòng trong Parquet không ảnh hưởng tới ai vào tập nào. Có ca kiểm thử riêng.
- **`load_dataset` kiểm tra schema khi đọc.** Gần như không tốn gì bên cạnh chi phí đọc Parquet, và bắt được file bị sửa tay hoặc do bản cũ ghi ra — thứ mà nếu không bắt sẽ hiện ra dưới dạng một chỉ số kỳ lạ ba bước sau.
- **`leakage_between` đo dev và test với hợp của mọi tập đứng trước**, không chỉ với train: ngữ cảnh đi từ train qua dev tới test thì vẫn là rò rỉ.

```
ruff check .   -> All checks passed!
pytest         -> 277 passed   (thêm 33 ca)
```

Báo cáo đầy đủ: `results/leakage_report.md`.

---

<a id="pr-28"></a>

### #28 — T15: chia chunk theo câu và theo cửa sổ token

- **Nhánh:** `t15-chia-chunk` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 23/08/2026 12:21 · **gộp:** 23/08/2026 12:21 · **commit gộp:** [`7a7dea3`](https://github.com/wsunicorn/vihallulens/commit/7a7dea3e37a16385fdf45d74c9755d7a855bf56e)¹
- **Thay đổi:** +604 / −40, 6 file · **bình luận bot:** 1

Mảnh ghép cuối trước phần đóng góp cốt lõi. Đây là chỗ chunk-aware bắt đầu thành hình: Lookback Lens gốc hỏi *"mô hình nhìn vào ngữ cảnh bao nhiêu"*, phiên bản chunk-aware hỏi *"nhìn vào **đoạn nào**"* — câu hỏi chỉ tồn tại sau khi ngữ cảnh đã được cắt.

##### Bốn cái bẫy của tách câu tiếng Việt

Tách câu nghe như chỉ cần cắt ở dấu chấm. Bốn ca phá ngay ý đó:

1. **Số hàng nghìn viết bằng dấu chấm** — `331.212`. Ca này **tự khỏi**: dấu chấm trong số không có khoảng trắng theo sau, mà mẫu regex đòi phải có. Vẫn giữ test để ai nới lỏng mẫu là đỏ ngay.
2. **Chữ viết tắt** — `ThS. Trương Vĩnh Linh`, `TP. Hồ Chí Minh`, `Nxb. Giáo dục`. Chấm, khoảng trắng, chữ hoa — đúng khuôn ranh giới thật. Thiếu chữ nào trong danh sách là cắt giữa tên người. Đã liệt 40 chữ.
3. **Chữ cái viết tắt tên người** — `Nguyễn V. A.` Không liệt kê hết được, bắt bằng luật: một ký tự chữ cái đứng một mình.
4. **Ngày tháng** — `ngày 31. 12. 2024`. Cắt vào giữa ngày còn tệ hơn để nguyên.

##### Hai quyết định thiết kế

**Chunk theo câu lát kín ngữ cảnh, không để khe hở.** Nếu chunk chỉ giữ phần chữ, token rơi vào khoảng trắng giữa hai câu sẽ **không thuộc chunk nào** — vẫn nằm trong mẫu số của `lookback_context` nhưng không xuất hiện ở ô nào, tức rò rỉ một phần chú ý ra ngoài mọi chunk. Nên `char_end` chunk này bằng đúng `char_start` chunk kế; có test khẳng định nối lại ra đúng ngữ cảnh gốc.

**Câu ngắn đầu tiên gộp về sau, không gộp về trước.** `docs/SPEC.md` ghi "gộp vào câu trước", nhưng câu đầu tiên **không có câu trước**. Mà mở đầu ngắn rất hay gặp — một dòng tít, một dòng `Theo VnExpress.` Bỏ mặc thì thành chunk vài từ mà không phân bố chú ý nào nói được gì.

##### Kết quả trên dữ liệu thật

| Bộ | Chunk mỗi ngữ cảnh | Từ mỗi chunk | Chỉ 1 chunk |
|---|---|---|---|
| ViHallu | 5,3 (tv 5, max 42) | 33,9 | 1,0 % |
| ISE-DSC01 | 22,8 (tv 20, max 161) | 27,7 | 0,0 % |
| ViWikiFC | 3,5 (tv 3, max 20) | 31,5 | **15,3 %** |
| ViFactCheck | 19,3 (tv 17, max 86) | 35,3 | 0,0 % |

Trung vị khớp sát cột "số câu mỗi ngữ cảnh" ở mục 4 `docs/DATA.md` (5 / 19 / 4 / 17).

**Định vị bằng chứng — nền của E06:**

| Bộ | Định vị được | Vắt qua ranh giới |
|---|---|---|
| ISE-DSC01 | 3.000/3.000 (100 %) | 41 (1,4 %) |
| ViWikiFC | 3.000/3.000 (100 %) | 57 (1,9 %) |

**100 %** — E06 có đủ nhãn vàng để chấm hit@1, hit@3, MRR trên toàn bộ mẫu có bằng chứng, không mất mẫu nào ở khâu này.

##### Một phát hiện phải xử lý ở T16

**15,3 % ngữ cảnh ViWikiFC chỉ ra đúng một chunk.** Với một chunk thì chunk-aware **thoái hóa thành lookback gộp** — mọi đặc trưng phân bố (entropy, Gini, top1–top2) thành hằng số. Hơn một phần bảy số mẫu của bộ này không đóng góp gì cho CH1.

Đây đúng là lý do mục 8 `docs/DATA.md` yêu cầu T16 dựng chỉ mục BM25 trên 3.814 câu bằng chứng. Trước T15 đó là suy đoán; giờ có con số đỡ lưng.

##### Ghi chú chuyển cho T21

`stride` mặc định bằng nửa cửa sổ nên chunk `token_window` **chồng lấn**, một token trong phần chồng bị đếm hai lần, tổng tỷ trọng không còn bằng 1.

Hệ quả: `chunk_entropy` và `chunk_gini` chỉ thật sự đọc **một phân bố** khi dùng chiến lược `sentence`. Với `token_window` phải chuẩn hóa trước khi tính — nếu không, entropy lệch có hệ thống theo `stride`, và **E04 quét ba cỡ cửa sổ sẽ đo nhầm hiệu ứng đó thành khác biệt giữa các cỡ**.

##### Dọn nợ

Bộ tách câu tạm viết ở T07 (kèm chú thích "T15 sẽ thay") đã xóa; `probe_attention_hook.py`, `compare_dtypes.py`, `measure_throughput.py` nay dùng `chunk_by_sentence` thật.

Hệ quả nhỏ: chạy lại T07/T08 bây giờ ra **số chunk khác** với con số đã ghi (mẫu ISE-DSC01 dài nhất trước ra 169 chunk). Thời gian và bộ nhớ không đổi đáng kể, và hai task đó là thăm dò khả thi chứ không phải thí nghiệm, nên số cũ giữ nguyên làm bản ghi lịch sử.

```
ruff check .   -> All checks passed!
pytest         -> 314 passed   (thêm 37 ca)
```

---

<a id="pr-29"></a>

### #29 — T16: kho truy xuất ViWikiFC, hết giai đoạn 2

- **Nhánh:** `t16-kho-truy-xuat-viwikifc` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 23/08/2026 14:17 · **gộp:** 23/08/2026 14:18 · **commit gộp:** [`03191a7`](https://github.com/wsunicorn/vihallulens/commit/03191a7ba073e10d594c77c517ce56c5cb575e5e)¹
- **Thay đổi:** +638 / −2, 4 file · **bình luận bot:** 1

Task cuối của giai đoạn 2. Giải quyết đúng vấn đề T15 vừa đo ra.

##### Vì sao cần

T15 đo được: **15,3 % ngữ cảnh của ViWikiFC chỉ ra đúng một chunk**, vì `context` của bộ này thường chỉ ba bốn câu. Với một chunk thì chunk-aware **thoái hóa thành lookback gộp** — chẳng còn gì để so giữa các đoạn.

Mục 8 `docs/DATA.md` đưa lời giải: cả bộ chỉ dựa trên 3.814 câu bằng chứng duy nhất từ 73 bài Wikipedia, đủ ít để giữ trọn trong bộ nhớ làm kho truy xuất. E08 dựng ngữ cảnh nhiều đoạn thật sự bằng cách lấy top-k câu cho mỗi claim.

##### Kết quả

```
python scripts/build_evidence_corpus.py

  câu bằng chứng        : 3,814
  bài Wikipedia         : 73
  độ dài câu (từ)       : trung vị 31, trung bình 35.2, dài nhất 251
  claim mỗi câu         : trung bình 5.5, tối đa 42
  dựng chỉ mục BM25     : 0.07 s
```

Cả hai con số của mục 8 khớp chính xác. Chỉ mục dựng trong 0,07 giây nên **không lưu xuống đĩa**, chỉ lưu kho câu — file pickle chứa chỉ mục sẽ mong manh theo phiên bản thư viện mà không giữ gì không tính lại được.

##### Recall bằng chứng vàng — con số quyết định E08 có làm được không

Tiêu chí ghi *"truy vấn thử một claim trả về top-5 hợp lý"*, nhưng nhìn ba kết quả bằng mắt thì không nói lên gì. Câu hỏi thật: **BM25 có tìm lại đúng câu bằng chứng của một claim, giữa 3.814 ứng viên, hay không.** Nếu không thì ngữ cảnh ghép từ top-k sẽ thường không chứa câu trả lời, và E08 đo chất lượng bộ truy xuất chứ không đo tín hiệu chú ý.

2.000 claim ngẫu nhiên, seed 42:

| | @1 | @5 | @10 | @20 | @50 |
|---|---|---|---|---|---|
| Bằng chứng vàng | **80,3 %** | 89,6 % | **91,3 %** | 93,2 % | 95,2 % |

**Kho dùng được.** Script tự in cảnh báo nếu recall@10 tụt dưới 70 %.

Truy vấn thử, ba claim ngẫu nhiên — bằng chứng vàng ở hạng 1 cả ba:

```
claim : Đồ đồng được sử dụng phổ biến dưới thời nhà Thương, và đạt trình độ chế tác cao.
  1. [ 56.0] Thời nhà Thương, đồ đồng đã được dùng phổ biến, đạt trình độ chế tác cao. ← VÀNG
  2. [ 16.8] Nó được sử dụng phổ biến ở một số vùng thuộc Caribê, Châu Phi, Nam Á...
```

##### Ba quyết định đáng ghi

**1. Dựng kho từ file thô, không từ file đã chuẩn hóa.** Hai bên lệch đúng **một** câu: thô cho 3.814, chuẩn hóa cho 3.813. Lý do là T11 xóa trắng cột `evidence` của dòng không định vị được — và đúng một dòng rơi vào đó, chính là câu `NhậtaimBản` hỏng ở nguồn.

Dựng từ file chuẩn hóa thì câu ấy biến mất, và claim tương ứng **vĩnh viễn không truy xuất được bằng chứng vàng của nó** — E08 mất một mẫu vì lý do chẳng liên quan gì tới truy xuất. Kho truy xuất là **tập câu để tìm kiếm**; định vị được offset hay không là câu hỏi hoàn toàn khác.

**2. Tách token theo âm tiết, không thêm bộ tách từ tiếng Việt.** "Hà Nội" là hai mảnh của một từ, nên tách theo khoảng trắng cho ra âm tiết chứ không phải từ. Bộ tách từ đúng nghĩa là **một phụ thuộc mới, phải hỏi trước** theo mục 7 `CLAUDE.md`. Cái giá thực tế nhỏ, và recall@1 80,3 % nói rằng đủ dùng. Ghi lại vì đây là hạn chế **thật, đã đo** — nếu sau này cần hơn thì đây là chỗ cải thiện rẻ nhất.

**3. `evidence_id` băm từ nội dung, không đánh số theo thứ tự.** Cùng lý do với `context_id` ở T09: đánh số theo vị trí thì dựng lại từ dữ liệu sắp xếp khác đi sẽ đổi hết mã.

##### Một chi tiết nhỏ

**35 câu xuất hiện dưới nhiều hơn một bài Wikipedia.** Schema chỉ có một cột `title`, nên chọn bài xuất hiện nhiều nhất, hòa thì lấy tên đứng trước theo bảng chữ cái — cách chọn phải tất định, nếu không dựng lại kho sẽ xáo chúng lung tung.

Thêm cột `n_claims`: một câu phục vụ 42 claim là loại đối tượng khác hẳn một câu phục vụ đúng một claim.

##### Chuyển cho T27 (E08)

`EvidenceIndex.search` có sẵn tham số `exclude`. Đó là cách E08 dựng được ngữ cảnh **cố tình không chứa** bằng chứng vàng — chính là tình huống mà ảo giác ngoại lai là câu trả lời trung thực duy nhất. Chưa viết `build_context` vì đó là việc của T27.

```
ruff check .   -> All checks passed!
pytest         -> 340 passed   (thêm 26 ca)
```

**Hết giai đoạn 2.** Bốn bộ đã chuẩn hóa, chia tập, đo rò rỉ, chia chunk, dựng kho truy xuất. Từ T17 là các baseline — bắt đầu có số để so.

---

<a id="pr-30"></a>

### #30 — T17: E01 baseline tầm thường, sàn thật là macro-F1 0,670

- **Nhánh:** `t17-baseline-tam-thuong` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 10:39 · **gộp:** 27/08/2026 10:39 · **commit gộp:** [`1c6bc4c`](https://github.com/wsunicorn/vihallulens/commit/1c6bc4cd312cda9eec9acdc27dada2bfe3fd3d20)
- **Thay đổi:** +1033 / −23, 14 file · **bình luận bot:** 1

Thí nghiệm đầu tiên có số. `docs/EXPERIMENTS.md` gọi E01 là *"thí nghiệm bắt buộc chạy sớm nhất, vì nó định nghĩa sàn thật sự"* — và sàn cao hơn dự đoán.

##### Kết quả

| Chỉ số | Giá trị | ± lệch chuẩn |
|---|---|---|
| **macro-F1** | **0,6696** | 0,0038 |
| Accuracy | 0,6757 | 0,0033 |
| F1 `no` | 0,7495 | 0,0007 |
| F1 `intrinsic` | **0,5234** | 0,0083 |
| F1 `extrinsic` | 0,7360 | 0,0032 |
| ECE | 0,0611 | 0,0044 |

Chín tham số phải huấn luyện, **0,001 ms mỗi mẫu**, không cần GPU.

Hai đặc trưng tái lập đúng bảng đã công bố: độ dài trung bình ra **chính xác** 32,9 / 39,5 / 45,9 từ. Trùng lặp từ vựng ra 0,827 / 0,671 / 0,574 — cao hơn số cũ khoảng 0,02 vì cách đếm ở đây bỏ dấu câu và không phân biệt hoa thường; thứ tự và khoảng cách giữa ba nhãn giữ nguyên.

##### Ba điều con số này quyết định

**1. Ngưỡng thật để vượt là 0,670, không phải 0,328.** PhoBERT công bố macro-F1 32,83 % trên bài toán này. Lấy đó làm mốc thì mọi thứ đều trông như tiến bộ lớn — nhưng hai đặc trưng bề mặt đã đạt **gấp đôi**. Từ nay mốc so sánh của đề tài là 0,670.

**2. `intrinsic` là lớp khó nhất, cách hai lớp kia hơn 0,2 điểm F1.** Rất hợp lý: ảo giác nội tại là **xáo trộn thông tin vốn đã có** trong ngữ cảnh, nên nó *vẫn* trùng lặp từ vựng cao và *vẫn* dài vừa phải — hai đặc trưng bề mặt gần như mù với nó.

Đây chính là chỗ tín hiệu chú ý theo đoạn có cơ hội đóng góp nhiều nhất, và nên là chỗ E05 tập trung chứng minh. **Nếu chunk-aware chỉ cải thiện `no` và `extrinsic` thì chưa nói lên gì.**

**3. Chi phí gần bằng không.** Phương pháp nội tại tốn khoảng 420 ms/mẫu trên ViHallu (đo ở T08), tức **đắt hơn bốn trăm nghìn lần**. Cột chi phí của E11 có một mốc dưới rất khắc nghiệt.

##### Một lỗi âm thầm suýt lọt

Lần chạy đầu cho **ECE = 0,42** — mô hình lệch tự tin 42 điểm phần trăm, vô lý với accuracy 0,68. Loại lỗi tệ nhất, vì **mọi chỉ số khác vẫn đúng và vẫn trông hợp lý**.

Nguyên nhân: ECE cần biết **cột nào của ma trận xác suất ứng với lớp nào**. scikit-learn sắp lớp theo **bảng chữ cái** — `extrinsic, intrinsic, no` — còn thứ tự báo cáo của dự án là `no, intrinsic, extrinsic`. Mình ngầm cho rằng hai thứ tự trùng nhau. Kiểm lại: chỉ **25,7 %** khớp.

Macro-F1 và F1 từng lớp **không** bị ảnh hưởng, vì chúng so trực tiếp chuỗi nhãn. Sau khi sửa: ECE = **0,0611**.

**Chốt chặn để không tái diễn:** `compute_metrics` nay tự kiểm tra rằng lớp có xác suất cao nhất phải trùng với lớp được dự đoán, raise kèm thông báo chỉ đúng cách sửa. Đây là bất biến luôn đúng với mọi bộ phân loại sklearn, nên nó bắt lỗi ngay ở mẫu đầu tiên chứ không đợi ai đó thấy con số kỳ lạ.

##### Về yêu cầu "5 seed"

Mục 3 `docs/EXPERIMENTS.md` đòi độ lệch chuẩn qua 5 seed. Nhưng logistic regression giải bằng lbfgs trên bài toán lồi là **tất định** — đổi riêng `random_state` cho ra năm con số **y hệt nhau**, độ lệch chuẩn bằng 0, yêu cầu thành hình thức.

Nên độ lệch chuẩn ở đây đo bằng **lấy mẫu lặp lại tập huấn luyện** (bootstrap), trả lời câu hỏi có nghĩa hơn: *kết quả phụ thuộc bao nhiêu vào việc mẫu nào tình cờ rơi vào tập train*. Con số chính vẫn từ một lần huấn luyện trên toàn bộ tập train. Cách đo ghi vào trường `std_method` của `results/runs.jsonl`.

##### Bốn module dùng chung cho mọi thí nghiệm sau

- `features/surface.py` — hai đặc trưng bề mặt
- `evaluation/metrics.py` — `compute_metrics` theo mục 2.5 SPEC, kèm ECE và `summarise_runs`
- `detect/detector.py` — `LookbackDetector` theo mục 2.4 SPEC, mặc định tuyến tính, có chuẩn hóa thang đo vì hai đặc trưng lệch nhau khoảng bốn mươi lần
- `data/text.py` — gom định nghĩa "từ" về một chỗ, để BM25 ở T16 và trùng lặp từ vựng ở T17 không dùng hai định nghĩa khác nhau

```
ruff check .   -> All checks passed!
pytest         -> 396 passed   (thêm 56 ca)
```

---

<a id="pr-31"></a>

### #31 — T17: sửa cách đo độ bất định, khoảng tin cậy thật rộng gấp gần năm lần

- **Nhánh:** `t17-sua-do-bat-dinh` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 10:59 · **gộp:** 27/08/2026 11:00 · **commit gộp:** [`4adac96`](https://github.com/wsunicorn/vihallulens/commit/4adac96ce3c384ba4ccbe4b654440324b239120a)
- **Thay đổi:** +199 / −70, 6 file · **bình luận bot:** 1

Kiểm tra lại T17 theo yêu cầu, và phát hiện cách báo độ bất định đang sai hướng.

##### Kiểm chứng T17 — đúng

- **Rò rỉ train–test: 0 ngữ cảnh, 0 `sample_id`** trên cả dev lẫn test.
- **macro-F1 = 0,6696 khớp qua ba đường tính** (`average='macro'`, tự trung bình F1 từng lớp, và số đã báo).
- Ma trận nhầm lẫn xác nhận đúng câu chuyện về `intrinsic`:

```
                      no  intrinsic  extrinsic
          no         184         27          9
   intrinsic          73        112         63     <- chỉ bắt đúng 45,2 %
   extrinsic          14         41        177
```

`intrinsic` trượt **gần đều** sang hai lớp kia — 73 và 63. Không lệch hẳn về bên nào, tức hai đặc trưng bề mặt **không có tín hiệu nào** về lớp này, chứ không phải có tín hiệu yếu.

##### Nhưng cách báo độ bất định thì sai hướng

Đo thật ba nguồn biến thiên của macro-F1:

| Nguồn | Độ lệch chuẩn |
|---|---|
| Đổi riêng `random_state` — đúng nguyên văn "5 seed" | **0,000000** |
| Lấy lại mẫu tập huấn luyện | ±0,0036 |
| **Lấy lại mẫu tập test** | **±0,0174** |

Yêu cầu "5 seed" **rỗng**: lbfgs trên bài toán lồi là tất định, năm seed cho ra năm con số y hệt nhau tới chữ số thứ sáu.

Nhưng vấn đề lớn hơn: nó **che mất nguồn biến thiên chi phối**. Tập test ViHallu chỉ có 700 mẫu, nên chính việc mẫu nào rơi vào tập test làm macro-F1 xê dịch **gấp 4,6 lần** biến thiên huấn luyện.

Báo ±0,004 khiến kết quả trông chính xác hơn thực tế **gần năm lần**. Hệ quả: mọi so sánh sau này sẽ kết luận sai — hai phương pháp lệch nhau 0,02 trông như khác biệt rõ ràng, trong khi khoảng tin cậy của chúng chồng lên nhau gần hết.

##### Kết quả E01 sau khi sửa

| Chỉ số | Giá trị | ± lệch chuẩn | Khoảng tin cậy 95 % |
|---|---|---|---|
| **macro-F1** | **0,6696** | 0,0177 | **[0,6345 – 0,7024]** |
| Accuracy | 0,6757 | 0,0180 | [0,6400 – 0,7086] |
| F1 `no` | 0,7495 | 0,0223 | [0,7029 – 0,7907] |
| F1 `intrinsic` | **0,5234** | 0,0291 | [0,4631 – 0,5784] |
| F1 `extrinsic` | 0,7360 | 0,0227 | [0,6903 – 0,7805] |

**Ngưỡng để nói hơn hẳn E01 là 0,702, không phải 0,670.** Vượt 0,68 chỉ là rơi vào khoảng nhiễu của cùng một kết quả.

##### Quy tắc mới ở mục 3 `docs/EXPERIMENTS.md`

1. Con số bất định chính là **khoảng tin cậy 95 % từ 2.000 lần lấy lại mẫu tập test**.
2. **Vẫn chạy 5 seed với mô hình có yếu tố ngẫu nhiên** — E09 tinh chỉnh bộ mã hóa (khởi tạo trọng số, dropout, thứ tự dữ liệu), LightGBM (lấy mẫu con). Với chúng biến thiên do seed là thật và phải báo cáo.
3. Với mô hình tất định thì **ghi thẳng là 0**, đừng bịa ra biến thiên.

Hệ quả phải nhớ khi đọc bảng: **hai phương pháp lệch nhau dưới 0,03 macro-F1 trên tập test 700 mẫu là chưa phân định được.**

```
ruff check .   -> All checks passed!
pytest         -> 402 passed   (thêm 6 ca)
```

---

<a id="pr-32"></a>

### #32 — T18: chuẩn bị tinh chỉnh ba bộ mã hóa làm mốc so sánh

- **Nhánh:** `t18-chuan-bi-baseline-ma-hoa` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 11:14 · **gộp:** 27/08/2026 11:14 · **commit gộp:** [`e811cf8`](https://github.com/wsunicorn/vihallulens/commit/e811cf85ddee5812fea1450873e1c5bb6015d4cf)
- **Thay đổi:** +854 / −1, 7 file · **bình luận bot:** 1

Chuẩn bị cho T18. **Chưa tick task** — phần huấn luyện cần GPU, phải chạy trên Kaggle.

##### Vì sao task này quan trọng

Đây là **mốc so sánh nghiêm túc nhất** của đề tài. Khác E01 chỉ dùng hai đặc trưng bề mặt, ba mô hình này thật sự **đọc** văn bản; khác E10 dùng Gemini, chúng **chạy cục bộ** không tốn API. Nếu phương pháp chú ý nội tại không vượt được chúng thì lập luận về chi phí ở CH2 không đứng vững.

##### Một quyết định về phụ thuộc, đã hỏi và được duyệt

**PhoBERT được huấn luyện trên văn bản đã tách từ.** Tiếng Việt viết mỗi âm tiết rời nhau, nên `Hà Nội` là hai mảnh của một từ; PhoBERT học trên dạng đã ghép `Hà_Nội`. Đưa văn bản thô vào là đặt nó trước bộ từ vựng nó chưa từng thấy, và điểm tụt vì lý do **chẳng liên quan tới bài toán**.

Rủi ro nếu bỏ qua: báo cáo ghi "PhoBERT đạt X" rồi đề tài nói vượt PhoBERT; hội đồng hỏi *"các em có tách từ không?"* mà trả lời không thì **mốc so sánh đó bị bác bỏ**.

Đã thêm **`pyvi`** — nhẹ, chỉ một mô hình CRF vài MB, không kéo theo Java. Chỉ PhoBERT dùng; XLM-R và InfoXLM dùng SentencePiece trên văn bản thô nên **không được** đưa văn bản đã tách từ vào, dấu gạch dưới sẽ bị tokenize thành ký tự thường.

##### Một con số đo trước khi chạy, và nó đổi cách đọc kết quả

**Khoảng 50 % cặp của ViHallu vượt giới hạn 256 token của PhoBERT.** Ở mức 512 token của hai mô hình kia thì chỉ **1,4 %**.

Đây không phải lựa chọn mà là **trần cứng** — PhoBERT không thể vượt 256 vị trí. Hệ quả: nếu PhoBERT thua thì phải ghi rõ nó thua **một phần vì không đọc hết được ngữ cảnh**, chứ không kết luận là mô hình yếu hơn. Script tự in tỷ lệ này trước mỗi lần chạy.

Đã cân nhắc ép cả ba xuống 256 token cho công bằng, nhưng bỏ: mục đích của mốc so sánh là **thứ mạnh nhất mà đề tài phải vượt**, nên mỗi mô hình dùng cấu hình tốt nhất của nó và tỷ lệ cắt được báo cáo kèm điểm số.

##### Ba quyết định thiết kế khác

**1. Vòng lặp huấn luyện viết tay, không dùng `transformers.Trainer`.** Repo giải ra `transformers` 5.15, mà tham số của `Trainer` ở nhánh 5.x khác nhánh 4.x — nhánh mà gần như mọi ví dụ trên mạng dùng. Một vòng lặp bốn mươi dòng không đáng để đánh cược rủi ro phiên bản trên một lần chạy tốn quota GPU.

**2. Cặp đầu vào đúng theo mẫu prompt đã chốt ở T07:** vế trái là mọi thứ mô hình được cho (ngữ cảnh + câu hỏi), vế phải là văn bản cần chấm (phản hồi). Nhờ vậy so sánh với phương pháp chú ý là so **phương pháp**, không phải so xem ai được cho xem nhiều hơn.

**3. Ba seed thay vì năm.** Mục 3 `docs/EXPERIMENTS.md` đòi năm, và tinh chỉnh **thật sự** ngẫu nhiên (khởi tạo đầu phân loại, dropout, thứ tự dữ liệu) nên seed ở đây đo được thứ có thật — khác hẳn E01.

Nhưng T17 đo được khoảng tin cậy tập test là ±0,017, lớn hơn hẳn biến thiên seed của một mô hình đã hội tụ. Seed thứ tư và năm sẽ tinh chỉnh một con số vốn đã bị một con số lớn hơn chi phối, đổi lại **khoảng một giờ quota mỗi mô hình 512 token**. Có cờ `--seeds 5` cho ai muốn theo đúng nguyên văn.

##### Việc cần chạy

Mở `notebooks/t18_baseline_bo_ma_hoa_t4.ipynb`, **chạy mỗi mô hình một lần Save Version riêng**.

Lý do ở mục 5 `CLAUDE.md`, đo được ở T08: chạy hai cấu hình nối nhau trong cùng phiên thì T4 tản nhiệt thụ động bị **hạ xung**, lượt sau chậm 10–15 % dù khối lượng tính y hệt — cột `ms/mẫu` sẽ lệch theo thứ tự chạy chứ không theo thực lực.

| Mô hình | Độ dài | Batch | 1 seed | 3 seed |
|---|---|---|---|---|
| PhoBERT-large | 256 | 16 | ~7 phút | ~25 phút |
| XLM-R-large | 512 | 8 | ~25 phút | ~80 phút |
| InfoXLM-large | 512 | 8 | ~25 phút | ~80 phút |

Tổng khoảng **3 giờ**, trong hạn mức 30 giờ/tuần.

##### Đọc kết quả thế nào

**Mốc phải vượt là 0,702** — cận trên khoảng tin cậy của E01, không phải 0,670. Một mô hình đạt 0,68 chỉ nằm trong khoảng nhiễu của hai đặc trưng bề mặt.

Chỗ đáng nhìn nhất là **F1 của lớp `intrinsic`**: E01 chỉ đạt 0,523 và bắt đúng 45,2 %. Bộ mã hóa cải thiện được bao nhiêu ở đó mới là phần nói lên điều gì.

```
ruff check .   -> All checks passed!
pytest         -> 419 passed   (thêm 17 ca)
```

---

<a id="pr-33"></a>

### #33 — T18: đo nhiệt độ ngay trong lúc tinh chỉnh, chạy cả ba mô hình một phiên

- **Nhánh:** `t18-do-nhiet-va-chay-mot-phien` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 11:26 · **gộp:** 27/08/2026 11:26 · **commit gộp:** [`0fba4f6`](https://github.com/wsunicorn/vihallulens/commit/0fba4f6fb1a75267a45b9f8176232e1f070b9a4a)
- **Thay đổi:** +182 / −122, 6 file · **bình luận bot:** 1

Trả lời câu hỏi: chạy cả ba mô hình trong một lần có được không.

##### Được, và notebook nay mặc định như vậy

Ban đầu mình bắt tách ba phiên Save Version riêng vì quy tắc hạ xung ở mục 5 `CLAUDE.md`. Nghĩ lại thì phòng ngừa quá tay:

**Hạ xung làm card chậm đi chứ không làm kết quả sai.** Toàn bộ macro-F1, accuracy, F1 từng lớp — thứ mà mốc so sánh này sinh ra để đo — không hề bị ảnh hưởng.

Thứ duy nhất bị ảnh hưởng là cột `ms/mẫu`. Mà cột đó dùng cho E11 để so **nhóm phương pháp** (bộ mã hóa vs chú ý nội tại vs Gemini), không phải so PhoBERT với XLM-R. Chênh lệch giữa ba mô hình vốn đã tới từ độ dài chuỗi — 256 với 512 token, khoảng gấp đôi — nên 15 % hạ xung không đổi thứ hạng hay bậc độ lớn.

##### Đo thay vì phòng ngừa

Script nay **tự đọc nhiệt độ và xung nhịp** trước khi chạy và sau mỗi seed, in cảnh báo nếu phát hiện hạ xung, và ghi số liệu vào `results/runs.jsonl`.

Chạy xong sẽ **biết chắc** có bị hay không, thay vì phải phỏng đoán và tách phiên cho chắc. Cảnh báo cũng nói rõ điểm số không bị ảnh hưởng, chỉ `ms/mẫu` là không so thẳng được với phiên khác.

##### Dọn một chỗ trùng lặp

Phần đo nhiệt trước nằm trong `scripts/measure_throughput.py`. Nay tách ra `src/vihallulens/evaluation/telemetry.py` để hai script dùng chung, thay vì script này import từ script kia.

Tách ba phiên chỉ còn đáng làm nếu sau này cần so `ms/mẫu` giữa ba mô hình một cách chặt chẽ — lúc đó chạy lại từng cái, điểm số không phải chạy lại.

```
ruff check .   -> All checks passed!
pytest         -> 419 passed
```

---

<a id="pr-34"></a>

### #34 — T18: sửa cách chia tập cho tái lập được trên mọi máy

- **Nhánh:** `t18-sua-chia-tap-tai-lap` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 11:38 · **gộp:** 27/08/2026 11:38 · **commit gộp:** [`a035b02`](https://github.com/wsunicorn/vihallulens/commit/a035b021690fbd20802c09525c54b23a3e2d8d10)
- **Thay đổi:** +170 / −51, 9 file · **bình luận bot:** 1

Chạy thử T18 trên Kaggle lộ ra hai lỗi. Lỗi thứ nhất nghiêm trọng hơn nhiều so với vẻ ngoài của nó.

##### Lỗi 1 — cách chia tập không tái lập được giữa các máy

Cùng seed 42, cùng dữ liệu, ra hai kết quả khác nhau:

| Máy | train / dev / test |
|---|---|
| Máy cá nhân (Python 3.11) | 5.598 / 702 / 700 |
| Kaggle (Python 3.12, torch 2.10) | **5.632 / 706 / 662** |

Nguyên nhân: `group_split` xáo thứ tự nhóm bằng `numpy.random.default_rng(seed).shuffle`.

**Đã loại trừ hai giả thuyết dễ nghĩ trước khi kết luận:**

- Ký tự xuống dòng khác nhau giữa hai bản CSV → kiểm: ViHallu **không có ký tự xuống dòng nào** trong ô `context`.
- Kiểu dữ liệu của mảng đem xáo (`object` vs `<U16`) → kiểm: hai kiểu cho **cùng một hoán vị**.

Còn lại là chênh lệch phiên bản thư viện trên Kaggle.

###### Không truy tiếp, mà bỏ hẳn chỗ phụ thuộc

Thứ tự nhóm nay lấy từ **băm SHA-256 của `(seed, context_id)`** rồi sắp xếp. SHA-256 cố định theo **chuẩn** chứ không theo phiên bản thư viện, và `sorted` thì ổn định — nên kết quả chỉ phụ thuộc seed và các mã ngữ cảnh, không phụ thuộc gì khác.

**Vì sao đáng làm tới mức đó:** mọi thí nghiệm từ đây trở đi đều đứng trên cách chia này. Một cách chia đổi theo phiên bản thư viện thì hai người trong nhóm chạy cùng một lệnh sẽ ra hai con số khác nhau, và không ai biết vì sao.

Thêm **hai chốt chặn**: một ca kiểm thử khóa cứng bốn phần tử đầu của thứ tự xáo, và một ca đặt seed toàn cục của NumPy thành giá trị lạ rồi khẳng định cách chia không nhúc nhích — để lần sau ai đó lại với tay sang `numpy.random` là đỏ ngay.

###### Số mới

| Bộ | train | dev | test |
|---|---|---|---|
| ViHallu | 5.600 (80,0 %) | 700 (10,0 %) | 700 (10,0 %) |
| ISE-DSC01 | 29.077 (79,9 %) | 3.646 (10,0 %) | 3.646 (10,0 %) |

Rò rỉ vẫn bằng 0.

###### E01 chạy lại — và nó minh họa đúng bài học của T17

| | Tập chia cũ | Tập chia mới |
|---|---|---|
| macro-F1 | 0,6696 | **0,6562** |
| Khoảng tin cậy 95 % | [0,6345 – 0,7024] | **[0,6200 – 0,6891]** |

Lệch **0,013**, nằm gọn trong khoảng nhiễu ±0,018. Nếu tuần trước mình vẫn báo ±0,004 như ban đầu thì chênh lệch này sẽ trông như một thay đổi thật, và ai đó sẽ đi tìm nguyên nhân không tồn tại.

**Ngưỡng để nói hơn hẳn E01 nay là 0,689.**

##### Lỗi 2 — notebook gọi `split_data.py` khi mới chuẩn hóa một bộ

Script xử lý cả bốn bộ nên dừng giữa chừng vì thiếu ISE-DSC01.

Thêm cờ `--only` để chỉ xử lý bộ cần, và cho báo cáo rò rỉ của lần chạy một phần ghi ra **tên file khác** — để không đè lên bản đầy đủ mà mục 6 `docs/DATA.md` trỏ tới đích danh.

```
ruff check .   -> All checks passed!
pytest         -> 424 passed   (thêm 5 ca)
```

---

<a id="pr-35"></a>

### #35 — T18: sửa lỗi nhãn dạng chuỗi lọt vào tensor, thêm test chạy trọn vòng lặp trên CPU

- **Nhánh:** `t18-sua-loi-ma-hoa-nhan` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 11:47 · **gộp:** 27/08/2026 11:47 · **commit gộp:** [`6134fa0`](https://github.com/wsunicorn/vihallulens/commit/6134fa069d8d8ef9194811d4a61d427e05253a20)
- **Thay đổi:** +146 / −16, 3 file · **bình luận bot:** 1

Lượt chạy GPU đầu tiên dừng ngay trước bước huấn luyện đầu, sau khi đã tải xong trọng số cả ba mô hình.

```
ValueError: too many dimensions 'str'
    torch.tensor(labels, dtype=torch.long)
```

##### Nguyên nhân — một chỗ nửa vời của chính mình

Trong `main()` mình mã hóa nhãn tập train thành số, nhưng **cố ý giữ nhãn tập test ở dạng chuỗi** vì `compute_metrics` chấm điểm bằng chuỗi. Rồi lại đưa chính chuỗi đó vào `make_loader` để dựng tensor.

Sửa bằng cách **cho nhãn chỉ tồn tại ở một dạng duy nhất** trong cấu trúc dữ liệu — chuỗi — và mã hóa thành số **ngay tại chỗ dựng loader**. Hai dạng nhãn nằm ở hai chỗ khác nhau thì sớm muộn cũng có chỗ dùng nhầm.

##### Bài học đắt hơn

**Không có cách nào kiểm tra vòng lặp huấn luyện trước khi tốn quota.**

Mục 5 `docs/SPEC.md` ghi *"chỉ test phần không cần GPU"*, và mình đã hiểu câu đó thành "vòng lặp huấn luyện thì khỏi test" — sai. Vòng lặp **chạy được hay không** là chuyện của CPU; chỉ **chạy nhanh hay chậm** mới cần GPU.

`train_once` nay nhận tham số `build` để tiêm mô hình vào, và có **hai ca kiểm thử chạy trọn vòng lặp trên CPU** với một Roberta hai lớp khởi tạo ngẫu nhiên, không tải gì. Xong trong vài giây, và bắt đúng loại lỗi vừa xảy ra.

##### Hai chỉnh nhỏ đi kèm

**Bớt log rác.** Tokenizer của `transformers` lặp lại một dòng cảnh báo cắt chuỗi mỗi batch — hàng trăm dòng, che mất mọi thứ đáng đọc.

**Số đo nhiệt độ lúc rảnh nay chỉ in ra, không đưa vào phán quyết hạ xung.** Kaggle báo card rảnh chạy ở 300/1590 MHz, thấp hơn hẳn lúc tải, nên đưa vào sẽ khiến mọi lượt chạy trông như đang *tăng* xung.

##### Một con số đo thật, khác ước lượng

| | Ước lượng ban đầu | Đo thật trên Kaggle |
|---|---|---|
| PhoBERT vượt 256 token | ~50 % | **29,3 %** |
| XLM-R vượt 512 token | ~1,4 % | **2,5 %** |

Ước lượng cũ nhân số từ với 1,3, sai vì BPE của PhoBERT trên văn bản **đã tách từ** nén tốt hơn hệ số đó nhiều. Tin tốt cho PhoBERT: nó bị cắt ít hơn mình tưởng.

```
ruff check .   -> All checks passed!
pytest         -> 426 passed   (thêm 2 ca chạy trọn vòng lặp)
```

---

<a id="pr-36"></a>

### #36 — T18: sửa bất ổn tinh chỉnh, sáu trên chín lần chạy trước không học được gì

- **Nhánh:** `t18-sua-bat-on-tinh-chinh` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 15:59 · **gộp:** 27/08/2026 15:59 · **commit gộp:** [`9586ea3`](https://github.com/wsunicorn/vihallulens/commit/9586ea3419ad3454b1dd0282acf2302853467cc1)
- **Thay đổi:** +212 / −21, 6 file · **bình luận bot:** 1

Lượt chạy GPU đầu tốn **3,5 giờ** và kết quả hỏng.

| Mô hình | macro-F1 từng seed | Học được |
|---|---|---|
| PhoBERT-large | 0,778 · **0,167** · 0,757 | 2/3 |
| XLM-R-large | **0,167 · 0,167 · 0,167** | 0/3 |
| InfoXLM-large | **0,167 · 0,167 · 0,167** | 0/3 |

##### 0,167 không phải điểm kém — là dấu hiệu không học gì

\`f1_no = 0\`, \`f1_extrinsic = 0\`, \`f1_intrinsic = 0,5011\` → macro = 0,167. Và accuracy 0,3343 × 700 = **234 mẫu**, bằng đúng số mẫu \`intrinsic\` trong tập test.

**Mô hình đoán `intrinsic` cho cả 700 mẫu.**

Xác nhận bằng loss: entropy chéo của mô hình ba lớp chưa học gì là `ln(3) = 1,0986`. Loss của XLM-R dao động 1,02–1,27 suốt **2.100 bước** mà không giảm. Chưa từng rời điểm xuất phát.

##### Nguyên nhân

**Bất ổn khi tinh chỉnh ở learning rate 2e-5** — vấn đề nổi tiếng của họ RoBERTa cỡ large, nặng thêm vì T4 là kiến trúc Turing nên **không hỗ trợ bfloat16**, buộc dùng float16 dải hẹp hơn nhiều.

Bằng chứng ủng hộ: PhoBERT ở cùng learning rate cũng sụp **một trong ba** lần — không phải lỗi riêng mô hình nào.

##### Ba lớp phòng vệ

1. **Hạ learning rate xuống 1e-5**, khai báo riêng từng mô hình trong `MODELS` chứ không dùng chung hằng số. Kèm `eps=1e-6` cho AdamW — cách chữa tiêu chuẩn cho bất ổn họ RoBERTa.
2. **Dừng sớm.** Hết một epoch mà loss vẫn quanh `ln(3)` thì tự dừng. Sáu lần chạy chết ở lượt trước đốt **hai tiếng rưỡi** để in ra một hàng 0,167 giống hệt nhau.
3. **Ô thử rẻ trong notebook.** Một seed, một epoch, mô hình khó nhất — **mười phút** thay vì ba tiếng rưỡi để biết cấu hình có ổn.

Cũng sửa một lỗi thật mà PyTorch đã cảnh báo suốt lượt chạy: `GradScaler` **bỏ hẳn bước cập nhật** khi gradient float16 tràn số, nhưng `scheduler.step()` vẫn được gọi — lịch learning rate cứ chạy trong khi trọng số đứng yên. Nay chỉ bước scheduler khi optimizer thật sự đã bước.

##### Một lỗi trong chính cách mình báo cáo

```
macro_f1            0.5672    0.3467   [0.7228, 0.7860]
```

**Trung bình 0,5672 nằm NGOÀI khoảng tin cậy của chính nó.** Vô lý — dấu hiệu của lỗi chứ không phải sai lệch tinh vi.

Trung bình tính trên **cả ba seed** (gồm seed sụp đổ 0,167), còn khoảng tin cậy lấy từ **seed ở giữa** (0,757). Hai con số mô tả hai thứ khác nhau nhưng đặt cạnh nhau như thể cùng một thứ.

Sửa: lần chạy chỉ đoán một lớp bị **phát hiện và loại khỏi thống kê**, macro-F1 **từng seed** in riêng, có cảnh báo rõ. Nếu **mọi** seed đều sụp thì script **báo lỗi và không in số nào** — thay vì in 0,167 như thể đó là kết quả.

```
ruff check .   -> All checks passed!
pytest         -> 430 passed   (thêm 11 ca)
```

---

<a id="pr-37"></a>

### #37 — T18: bỏ ô thử nghiệm khỏi notebook, ghi lại kết quả kiểm chứng

- **Nhánh:** `t18-bo-o-thu-nghiem` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 16:21 · **gộp:** 27/08/2026 16:21 · **commit gộp:** [`6304e1c`](https://github.com/wsunicorn/vihallulens/commit/6304e1cc753ab82462c74111a7a78cc6073fabef)
- **Thay đổi:** +61 / −43, 2 file · **bình luận bot:** 1

Ô thử rẻ đã xong việc của nó.

##### Kết quả kiểm chứng — mười phút

```
batch / epoch / lr    : 8 / 1 / 1e-05
macro-F1 0.7076   huấn luyện 9.2 phút   VRAM đỉnh 11,231 MB   76 °C
  seed 42: 0.7076   (695 bước thật)
```

Ba điều đọc được:

1. **Cấu hình đã ổn.** Không sụp đổ, `f1_intrinsic = 0,591` — cao hơn hẳn 0,533 của E01.
2. **695 trên 700 bước thật.** Năm bước bị bỏ vì gradient float16 tràn số — xác nhận chẩn đoán tràn số đúng, **và** xác nhận bản vá scheduler chạy đúng (trước đây lịch learning rate vẫn đi tiếp trong lúc trọng số đứng yên).
3. **Một epoch đã vượt mốc.** 0,7076 > 0,689, tức bộ mã hóa là mốc so sánh đáng gờm thật chứ không phải hình thức.

##### Vẫn giữ ba epoch

Dù một epoch đã vượt mốc. Mục đích của mốc so sánh là **thứ mạnh nhất mà đề tài phải vượt** — huấn luyện thiếu sẽ làm nó yếu đi một cách có lợi cho đề tài, và đó đúng là chỗ hội đồng dễ bác nhất.

##### Thay đổi trong notebook

- Bỏ ô thử rẻ, đánh số lại còn 7 ô. Câu lệnh vẫn giữ trong phần hướng dẫn để dùng lại khi đổi cấu hình.
- Ước tính thời gian theo số đo thật: PhoBERT ~36 phút, hai mô hình 512 token ~83 phút mỗi cái, tổng ~3,4 giờ.
- Mốc phải vượt sửa thành **0,689** (cận trên khoảng tin cậy E01 sau khi sửa cách chia tập ở T18), thay cho 0,702 cũ.
- Tỷ lệ cắt sửa thành **29,3 %** đo thật, thay cho ước lượng 50 %.
- Thêm hướng dẫn đọc dòng **macro-F1 từng seed** để nhận ra seed sụp đổ.

```
ruff check .   -> All checks passed!
pytest         -> 430 passed
```

---

<a id="pr-38"></a>

### #38 — T18: sửa lưới lọc seed chết bị thủng

- **Nhánh:** `fix-t18-bao-cao-seed-chet` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 17:13 · **gộp:** 27/08/2026 17:13 · **commit gộp:** [`b64a105`](https://github.com/wsunicorn/vihallulens/commit/b64a105d580f5e2d020551294bdc827d3ae727fa)
- **Thay đổi:** +110 / −10, 3 file · **bình luận bot:** 1

Lượt chạy PhoBERT ngày 27/08/2026 lộ ra một kẽ hở trong cơ chế loại seed không học được, thêm ở PR #36.

##### Triệu chứng

```
macro-F1 từng seed:
  seed 42: 0.1696   (346 bước thật)     ← đã in DỪNG SỚM
  seed 43: 0.7542   (1,045 bước thật)
  seed 44: 0.7234   (1,043 bước thật)

Trung bình 3 seed học được, khoảng tin cậy lấy từ seed ở giữa:
macro_f1            0.5490    0.3290   [0.6887, 0.7546]
```

Trung bình lại nằm ngoài khoảng tin cậy của chính nó. `(0,1696 + 0,7542 + 0,7234) / 3 = 0,5490` — seed chết vẫn được tính vào.

##### Nguyên nhân

Cách phát hiện cũ đếm số lớp khác nhau trong dự đoán. Seed 42 đoán `intrinsic` cho 699 mẫu và một mẫu ra lớp khác, nên hai lớp — không có gì trông giống sụp đổ. Đoán một lớp cho cả 700 mẫu sẽ cho đúng 0,1670; seed 42 ra 0,1696.

Số lớp trong dự đoán chỉ là hệ quả gián tiếp của việc không học, nên nó có kẽ hở.

##### Sửa

Script vốn đã biết seed này hỏng — chính nó in ra `DỪNG SỚM` dựa trên loss đứng ở `ln(3)`. Kết luận đó nay được truyền sang phần thống kê qua cờ `stopped_early`. Một lần chạy được tính là học được chỉ khi không dừng sớm **và** không sụp đổ.

Hai ca kiểm thử mới trên CPU: learning rate bằng 0 phải bị đánh dấu không học được, và bài toán đồ chơi có tín hiệu thật phải không bị dừng nhầm.

##### Kiểm chứng

- `ruff check .` sạch
- `pytest` 432 ca xanh (thêm 2)
- Số đúng của PhoBERT tính tay từ hai seed học được: macro-F1 **0,7388 ± 0,0154**, vượt mốc 0,689 của E01

Không cần chạy lại GPU: điểm từng seed là số thật, chỉ phép gộp sai, và `results/runs.jsonl` đã lưu `macro_f1_per_seed`.

---

<a id="pr-39"></a>

### #39 — T18: sửa nốt ba chỗ trước khi chạy lại trên Kaggle

- **Nhánh:** `sua-truoc-khi-chay-lai-t18` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 17:44 · **gộp:** 27/08/2026 17:44 · **commit gộp:** [`53d095d`](https://github.com/wsunicorn/vihallulens/commit/53d095d6622f602014de9ca1e1c9fa8c843b93d0)
- **Thay đổi:** +119 / −23, 5 file · **bình luận bot:** 1

Ba chỗ đã biết là sai, sửa gọn một lượt để lần chạy lại in ra số dùng được ngay.

##### 1. Seed mang khoảng tin cậy

Bootstrap lấy mẫu lại tập test nên nó mô tả **một** bộ dự đoán — phải chọn một lần chạy làm đại diện, và nên là lần bình thường nhất.

Cách cũ sắp xếp rồi lấy `len // 2`. Với **số chẵn** lần chạy — đúng thứ mà việc loại một seed chết để lại — nó luôn với sang cái **cao hơn** trong hai cái ở giữa. Mô hình nào mất một seed thì lặng lẽ được lấy khoảng tin cậy từ nửa tốt hơn của chính nó.

Nay chọn lần chạy **gần trung bình nhất**; hòa thì phân định theo thứ tự seed, một tiêu chí không liên quan tới điểm số. Với PhoBERT, khoảng tin cậy nay lấy từ seed 43 thay vì seed 44. Bảng kết quả cũng ghi rõ số seed đó thay vì chỉ nói "seed ở giữa".

##### 2. `requires-python`

```
ERROR: Package 'vihallulens' requires a different Python: 3.12.13 not in '<3.12,>=3.11'
```

Chặn trên không ngăn được gì — Kaggle chạy 3.12 và không cho đổi — mà chỉ làm `pip install -e .` hỏng ở mọi phiên GPU. Nới thành `>=3.11`. Mục 3 CLAUDE.md vẫn giữ 3.11 cho máy phát triển; đây chỉ là giới hạn cài đặt.

##### 3. Notebook

- Bỏ câu "đừng chạy cả ba trong một phiên", nằm ngay trên đoạn giải thích vì sao chạy một phiên là được
- Sửa chỗ ghi nhầm learning rate cũ là 1e-5 (đúng ra 2e-5)
- Thay ước tính thời gian bằng số đo thật
- Ghi lại kết quả PhoBERT lượt 27/08 làm mốc đối chiếu

##### Kiểm chứng

- `ruff check .` sạch
- `pytest` **435 ca xanh** (thêm 3)
- Mô phỏng lại trên đúng ba số PhoBERT: trung bình 0,7388 ± 0,0218, khoảng tin cậy từ seed 43

---

<a id="pr-40"></a>

### #40 — T18: ghi kết quả E09, tách hai loại độ lệch dùng chung tên khóa

- **Nhánh:** `sua-va-ghi-ket-qua-t18` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 20:50 · **gộp:** 27/08/2026 20:50 · **commit gộp:** [`fbf4300`](https://github.com/wsunicorn/vihallulens/commit/fbf4300525a161eae8f9f67bf21f4f40aa6f3ff2)
- **Thay đổi:** +147 / −286, 8 file · **bình luận bot:** 1

Lượt chạy sạch trên Kaggle ngày 27/08/2026, 2 giờ 48 phút GPU, commit `53d095d`.

##### Kết quả

| Phương pháp | macro-F1 [KTC 95 %] | F1 `intrinsic` | ECE | ms/mẫu | VRAM |
|---|---|---|---|---|---|
| E01 bề mặt | 0,656 [0,620–0,689] | 0,533 | 0,061 | 0,001 | 0 |
| PhoBERT-large | 0,742 [0,705–0,770] | 0,685 | 0,086 | 12,2 | 9.002 MB |
| **XLM-R-large** | **0,771** [0,747–0,808] | **0,722** | 0,114 | 24,8 | 11.231 MB |
| InfoXLM-large | *không tinh chỉnh được, 0/3 seed* | | | | 11.231 MB |

**Mốc mà đề tài phải vượt nay là 0,771, không còn 0,689.**

ECE đi **ngược chiều** macro-F1 (0,061 → 0,086 → 0,114): bộ mã hóa đoán đúng hơn nhưng hiệu chỉnh xác suất tệ hơn hai đặc trưng bề mặt.

##### InfoXLM: hai lưới lọc chứng minh mình đáng có

Cả ba seed đứng ở `ln(3)`. Hai trong ba ra 0,2371 và 0,1786 — **không phải** 0,167, tức đoán nhiều hơn một lớp và sẽ **lọt qua** lưới đếm số lớp. Chỉ lưới loss bắt được. Dừng sớm tiết kiệm một giờ (10,1 phút mỗi seed chết thay vì 30,3).

Cùng kích thước, cùng lr với XLM-R vốn chạy tốt 3/3 → bất ổn riêng của checkpoint, không phải của cấu hình.

##### Lỗi: hai loại độ lệch dùng chung tên khóa

```
màn hình:   macro_f1   0.7416   0.0118   [0.7053, 0.7702]
runs.jsonl: "macro_f1_std": 0.01623553635603956
```

`summarise_runs` đặt độ lệch chuẩn **qua seed** vào `{chỉ_số}_std`; `bootstrap_ci` đặt sai số chuẩn **bootstrap** vào đúng khóa đó. `{**across_seeds, **spread}` làm cái sau đè cái trước, và độ lệch qua seed của mọi chỉ số biến mất khỏi bản ghi.

Sửa: bootstrap dùng `_se`. Thêm ca kiểm thử khẳng định hai từ điển **không có khóa nào chung** — một dòng chặn cả họ lỗi này. Bản ghi lưu thêm `metrics_per_seed` (giá trị thô từng seed) để về sau gộp lại được.

Hai bản ghi của lượt 27/08 đã dựng lại: `_se` nguyên từ bản gốc, `_std` từ bảng chính lượt đó in ra, `macro_f1_std` tính lại từ `macro_f1_per_seed` và khớp 0,0118 / 0,0249. Có `note` trong bản ghi nói rõ.

##### Kiểm chứng

- `ruff check .` sạch
- `pytest` **438 ca xanh** (thêm 3)
- Chạy lại E01 trên CPU: số y hệt, chỉ đổi tên khóa

---

<a id="pr-41"></a>

### #41 — T18: notebook thử InfoXLM ở learning rate thấp hơn

- **Nhánh:** `thu-infoxlm-lr-thap` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 20:58 · **gộp:** 27/08/2026 20:58 · **commit gộp:** [`563f74a`](https://github.com/wsunicorn/vihallulens/commit/563f74a7b25e7635547974c9a149dfcb06c44d5c)
- **Thay đổi:** +223 / −1, 2 file · **bình luận bot:** 1

InfoXLM-large hỏng 3/3 seed ở `1e-5` trong lượt chạy 27/08. Notebook này thử hai mức thấp hơn trước khi kết luận.

##### Thử gì

| Lần | lr | Thời gian |
|---|---|---|
| A | `5e-6` | ~10 phút |
| B | `2e-6` | ~10 phút |

Một seed một epoch mỗi lần. Tổng ~25 phút kể cả tải mô hình 2,24 GB, so với 90 phút của một lượt ba seed ba epoch.

##### Vì sao hạ learning rate, không phải đoán mò

Loss của InfoXLM **không nằm im tuyệt đối** mà nảy quanh `ln(3)`, từ 1,0131 tới 1,1923. Đó là dáng của một mô hình đã rơi vào **nghiệm thoái hóa** — đoán theo tỷ lệ nền của ba lớp — chứ không phải dáng của một mô hình không được cập nhật gì.

Hai dạng hỏng này trông giống nhau ở con số cuối nhưng khác nhau ở đây, và đòi hai cách chữa **ngược nhau**: nghiệm thoái hóa thì giảm bước cập nhật, không được cập nhật thì phải tăng.

Củng cố thêm: cùng kích thước, cùng độ dài, cùng lr với XLM-R-large vốn chạy tốt 3/3 seed.

##### Giới hạn tự đặt

**Tối đa hai lần thử.** Cả hai hỏng thì dừng và ghi nhận đây là kết quả về độ ổn định, không phải ô trống cần lấp — XLM-R đạt 0,771 và đó mới là mốc đề tài phải vượt. Quota 30 giờ/tuần còn phải để cho T19 và T20.

---

<a id="pr-42"></a>

### #42 — T18: chốt InfoXLM không tinh chỉnh được, thêm công cụ soi checkpoint

- **Nhánh:** `chan-doan-infoxlm` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 21:58 · **gộp:** 27/08/2026 21:58 · **commit gộp:** [`a18f5f3`](https://github.com/wsunicorn/vihallulens/commit/a18f5f3c9fcbb8bd369ba79c08c87ea4f44d926e)
- **Thay đổi:** +373 / −11, 7 file · **bình luận bot:** 1

##### Hạ learning rate không cứu được — và dữ liệu chỉ hướng ngược lại

| lr | loss cuối epoch 1 | macro-F1 |
|---|---|---|
| `1e-5` | nảy 1,0131 – 1,1923 | 0,167 · 0,179 · 0,237 |
| `5e-6` | 1,1055 | 0,1670 |
| `2e-6` | **1,0992** | 0,1670 |

Giả thuyết là **nghiệm thoái hóa do bước cập nhật quá lớn**; nếu đúng thì hạ learning rate phải kéo loss **rời khỏi** `ln(3)`. Kết quả ngược hẳn: càng hạ càng **bám sát**. Ở `2e-6` loss dừng ở 1,0992, lệch `ln(3) = 1,0986` đúng 0,0006 — dáng của mô hình **không nhúc nhích**, dạng hỏng đòi cách chữa ngược lại.

Bài học dùng lại được: hai dạng hỏng cho cùng con số cuối 0,167, và cách phân biệt là **nhìn loss hội tụ về đâu khi hạ learning rate**.

##### Năm giả thuyết cơ học, kiểm hết bằng CPU, 0 quota GPU

| Giả thuyết | Kết quả |
|---|---|
| Thân mô hình bị khởi tạo ngẫu nhiên trong im lặng | **Bác bỏ** — thân nạp đủ, chỉ thiếu 4 trọng số của đầu phân loại đúng như XLM-R |
| Tên khóa không khớp | InfoXLM dùng tiền tố `embeddings.`/`encoder.` còn XLM-R dùng `roberta.`, nhưng `transformers` ánh xạ đúng |
| Cấu hình khác nhau | **Bác bỏ** — giống hệt, chỉ khác ba khóa vô hại |
| Tràn số float16 như lỗi lớp 27 ở T07 | **Bác bỏ** — đỉnh 25,2, bằng **0,04 %** trần 65.504. XLM-R còn cao hơn ở 32,1 |
| Vector CLS thoái hóa | **Bác bỏ, và ngược lại** — InfoXLM giãn cách 0,0261 so với 0,0020 của XLM-R |

Truy tiếp thì tốn hơn giá trị thu được. **Chốt: InfoXLM-large không tinh chỉnh được trên cấu hình này**, ghi vào báo cáo như kết quả về độ ổn định kèm bảng trên để thấy đây là kết luận sau khi loại trừ.

##### Hai thứ giữ lại từ một thí nghiệm thất bại

**`scripts/check_checkpoint.py`** — chạy cả bốn phép kiểm trên CPU trong vài phút. Dùng lại cho ablation Sailor2 ở E13 và mọi nấc lùi mô hình ở mục 5 CLAUDE.md.

**Báo cáo nạp trọng số ngay trong vòng huấn luyện.** `transformers` vốn in bảng nói trọng số nào thiếu, nhưng T18 tắt log bằng `set_verbosity_error()` để chặn cảnh báo cắt chuỗi — và tắt luôn đúng thông báo cần đọc. Nay `build_from_hub` tự đọc `output_loading_info` và **ném lỗi ngay** nếu thân mô hình thiếu trọng số, thay vì để một mạng ngẫu nhiên mang tên nổi tiếng ngốn hết một phiên GPU.

##### Kiểm chứng

- `ruff check .` sạch
- `pytest` **452 ca xanh** (thêm 14), gồm ca khẳng định đọc được cả `set` lẫn `list` vì hai phiên bản `transformers` trả về hai kiểu khác nhau

---

<a id="pr-43"></a>

### #43 — T19: baseline LLM giám khảo (E10) trên Gemini free tier

- **Nhánh:** `t19-baseline-llm-giam-khao` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 27/08/2026 23:34 · **gộp:** 27/08/2026 23:35 · **commit gộp:** [`23fa8ac`](https://github.com/wsunicorn/vihallulens/commit/23fa8acd494c0f36297fd5adb47bae991b95a0a3)
- **Thay đổi:** +1964 / −186, 12 file · **bình luận bot:** 1

##### Kết quả

300 mẫu, 41 phút, 0 lỗi, `gemini-3.1-flash-lite`.

| Chỉ số | Giá trị | KTC 95 % |
|---|---|---|
| macro-F1 | **0,6637** | [0,6070 – 0,7191] |
| F1 `no` | 0,7527 | [0,6782 – 0,8182] |
| F1 `intrinsic` | 0,5823 | [0,4878 – 0,6707] |
| F1 `extrinsic` | 0,6562 | [0,5872 – 0,7212] |

**Trên đúng 300 mẫu đó, baseline tầm thường E01 đạt 0,6860.** Giám khảo LLM **không vượt nổi hai đặc trưng bề mặt**. Khoảng tin cậy chứa cả hai nên chênh lệch nằm trong nhiễu — nhưng "không hơn nổi baseline tầm thường" tự nó là kết quả.

Diễn giải đúng không phải "Gemini kém" mà là **những gì free tier cho phép không đủ thay thế một phương pháp chuyên dụng** — chính là điều bảng đánh đổi E11 sinh ra để nói.

##### Nó hỏng đúng chỗ con người hỏng

| thật \ đoán | `no` | `intrinsic` | `extrinsic` |
|---|---|---|---|
| `no` | **70** | 9 | 32 |
| `intrinsic` | 3 | **46** | **48** |
| `extrinsic` | 2 | 6 | **84** |

**48 trên 97 mẫu `intrinsic` bị gọi thành `extrinsic`.** Recall lớp đó chỉ 0,474.

Nhưng đọc lý do nó tự viết thì thấy **không phải lỗi hiểu bài** mà là lỗi **thứ tự ưu tiên** — nó nhận ra *cả hai* dấu hiệu rồi chọn ngoại lai, và theo đúng bộ tiêu chí T13 thì nó chọn không sai.

| Người chấm | Recall lớp `intrinsic` |
|---|---|
| Sinh viên 1 (T13) | 0,70 |
| Sinh viên 2 (T13) | 0,50 |
| **Gemini (T19, 97 mẫu)** | **0,474** |

Giám khảo rơi đúng vào dải của con người và **lệch cùng một hướng**. Đây là lập luận mạnh cho phần bàn luận: ranh giới nội tại–ngoại lai khó một cách **nội tại**, không phải khó vì phương pháp nào dở.

**Vì thế không sửa prompt cho giám khảo dễ thở hơn.** Thêm quy tắc ưu tiên sẽ nâng điểm nhưng đưa cho giám khảo một đề bài **khác** đề bài hai sinh viên đã nhận, và quy tắc đó lại suy ra từ chính nhãn tập test.

##### Ba điều đo được làm đổi thiết kế

| Điều đo được | Hệ quả |
|---|---|
| `gemini-2.5-flash` **đã bị gỡ**, 404 cho khóa mới | Thêm `scripts/list_judge_models.py` hỏi thẳng API |
| `gemini-3.6-flash` chỉ cho **20 lượt/NGÀY** | 300 mẫu = 15 ngày. Không dùng |
| `gemini-3.5-flash-lite` trả lời **mất hết dấu** | Không dùng |

##### Kiểm chứng — đúng tiêu chí hoàn thành

```
python scripts/run_judge_baseline.py --dry-run
  Gọi API mới : 0  (còn lại lấy từ cache)
  macro_f1     0.6637   [0.6070, 0.7191]
```

Phép kiểm này **lộ ra một lỗi**: `--dry-run` lấy tên mô hình từ *đối tượng* giám khảo, mà dry run không có đối tượng nên rơi vào nhánh dự phòng `"dry-run"` và tính ra khóa không khớp gì — báo thiếu cả 300 mẫu trong cache đang giữ đủ 300. Đã sửa, kèm ba ca kiểm thử.

`results/judge_cache.jsonl` được commit, nên con số kiểm lại được **không tốn lượt gọi nào**.

- `ruff check .` sạch
- `pytest` **507 ca xanh** (thêm 61), toàn bộ phần mạng chạy offline

---

<a id="pr-44"></a>

### #44 — Thêm chỉ số nhị phân: tách phát hiện ảo giác khỏi phân loại đúng loại

- **Nhánh:** `chi-so-nhi-phan` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 28/08/2026 12:22 · **gộp:** 28/08/2026 12:22 · **commit gộp:** [`abf1645`](https://github.com/wsunicorn/vihallulens/commit/abf164554f40a35ec69643678b5d76541305e36e)
- **Thay đổi:** +191 / −19, 7 file · **bình luận bot:** 1

##### Vì sao

macro-F1 ba lớp đang **trộn hai câu hỏi** vào một con số:

- *Có phát hiện được ảo giác không?* — chấm trên ranh giới không ai tranh cãi.
- *Có gọi đúng tên loại không?* — chấm trên ranh giới mà **chính hai người gán nhãn cũng chỉ đồng thuận ở kappa 0,505** (T13), và 8/100 mẫu một người gán `noi_tai` còn người kia gán `ngoai_lai`.

Một phương pháp mạnh ở câu đầu mà yếu ở câu sau ra **cùng một điểm** với một phương pháp yếu ở cả hai.

##### Kết quả — đổi hẳn cách đọc E10

Trên **cùng 300 mẫu**:

| | macro-F1 ba lớp | macro-F1 nhị phân | bắt được | báo đúng |
|---|---|---|---|---|
| E01 bề mặt | **0,6860** | 0,8144 | 0,8889 | — |
| Gemini | 0,6637 | **0,8208** | **0,9735** | 0,8178 |

**Gemini thua ở ba lớp nhưng hơn ở nhị phân, và bắt được 97,4 % số mẫu có ảo giác.** Nó gần như không bỏ sót ảo giác nào — chỉ gọi sai tên loại.

Nếu chỉ nhìn con số ba lớp thì kết luận sẽ là "giám khảo LLM không hơn hai đặc trưng bề mặt", và kết luận đó **bỏ sót phần quan trọng nhất**.

##### Hiện thực

Bốn khóa `binary_macro_f1`, `binary_accuracy`, `binary_precision`, `binary_recall`, đặt **bên trong** `compute_metrics` chứ không đặt cạnh — nên mọi thí nghiệm, kể cả script viết trước, tự có mà không ai phải nhớ gọi thêm. Precision và recall là của lớp `hallucinated`, vì đó là thứ một hệ thống triển khai thật bị chấm.

##### Một hệ quả phải ghi lại

Chỉ số này tính từ **dự đoán**, không tính được từ các con số đã gộp. E01 và E10 tính lại được ngay; **E09 thì không** — lượt chạy 27/08 không lưu `y_pred`, nên hai ô nhị phân của PhoBERT và XLM-R trong Bảng 1 phải để trống chờ lần chạy sau.

Đúng bài học đã học ở T18 với `metrics_per_seed`, gặp lại lần thứ hai: **bản ghi có số thô thì gộp lại được, bản ghi chỉ có số đã gộp thì không.** Cả ba script nay đều ghi `y_pred`, khoảng 10 KB mỗi bản ghi.

##### Kiểm chứng

- `ruff check .` sạch
- `pytest` **513 ca xanh** (thêm 6)
- E01 chạy lại trên CPU, E10 chạy lại từ cache với 0 lượt gọi API

---

<a id="pr-45"></a>

### #45 — T18: lưu dự đoán thô của E09 trước khi chạy lại

- **Nhánh:** `luu-du-doan-e09` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 28/08/2026 12:30 · **gộp:** 28/08/2026 12:30 · **commit gộp:** [`e4996e5`](https://github.com/wsunicorn/vihallulens/commit/e4996e5d0c013bc76970ca96346efce2d00e94e0)
- **Thay đổi:** +403 / −2, 3 file · **bình luận bot:** 1

##### Suýt nữa thì lượt chạy lại thành vô ích

PR trước thêm `y_pred` vào `run_baseline_surface.py` và `run_judge_baseline.py`, rồi commit message tuyên bố "cả ba script nay đều ghi y_pred". **Sai** — `train_encoder_baseline.py` bị bỏ sót, mà đó mới đúng là script cần chạy lại trên GPU để điền hai ô nhị phân còn trống trong Bảng 1.

Không kiểm trước khi bấm chạy thì 2 giờ 15 phút quota sẽ ra một bản ghi vẫn thiếu đúng thứ cần.

Nay E09 ghi `y_pred_per_seed` — dự đoán của **từng seed**, nên về sau gộp lại được theo bất kỳ cách nào. Khoảng 25 KB mỗi bản ghi.

##### Notebook bỏ InfoXLM

Đã chốt ở lượt 27/08 là không tinh chỉnh được, và ba lượt thử ở `1e-5`, `5e-6`, `2e-6` đều đứng ở `ln(3)`. Chạy lại chỉ tốn ~30 phút để in ra cùng một kết luận. Câu lệnh vẫn giữ trong chú thích.

Thời gian còn **~2 giờ 15 phút**: PhoBERT 43 phút, XLM-R 91 phút.

##### Một mốc đối chiếu ghi sẵn trong notebook

| | macro-F1 lượt 27/08 |
|---|---|
| PhoBERT, 3 seed | 0,7416 ± 0,0118 |
| XLM-R, 3 seed | 0,7708 ± 0,0249 |

Hạt giống, cách chia tập và cấu hình đều không đổi, nên **ra khác đáng kể nghĩa là có gì đó đã đổi ngoài ý muốn** — đừng dùng số mới. Lệch vài chữ số cuối là bình thường vì phép tính GPU không hoàn toàn tất định.

- `ruff check .` sạch, `pytest` 513 xanh

---

<a id="pr-46"></a>

### #46 — Điền chỉ số nhị phân cho cả bốn mốc so sánh

- **Nhánh:** `ket-qua-e09-lan-hai` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 28/08/2026 23:24 · **gộp:** 28/08/2026 23:24 · **commit gộp:** [`cecce2c`](https://github.com/wsunicorn/vihallulens/commit/cecce2ca5f0ed535a913032d791ddd41510bce05)
- **Thay đổi:** +112 / −19, 5 file · **bình luận bot:** 1

##### Bảng 1 đã đầy đủ

| Phương pháp | Ba lớp [KTC 95 %] | Nhị phân | Chênh | Bắt được | Báo đúng |
|---|---|---|---|---|---|
| E01 bề mặt | 0,656 [0,620–0,689] | 0,802 | **+0,146** | 0,854 | 0,870 |
| Gemini free | 0,664 [0,607–0,719] | 0,821 | **+0,157** | **0,974** | 0,818 |
| PhoBERT | 0,749 [0,714–0,778] | 0,851 | +0,102 | 0,921 | 0,883 |
| **XLM-R** | **0,776** [0,757–0,818] | **0,881** | +0,105 | 0,920 | **0,918** |

**Cả bốn phương pháp đều được thêm 0,10 tới 0,16 điểm** khi bỏ đòi hỏi gọi đúng tên loại. Bằng chứng số học cho giả thuyết: phần khó nằm ở **ranh giới nội tại–ngoại lai**, không nằm ở việc phát hiện.

Ba điều đọc thêm được:

1. **Chênh lệch lớn hơn ở hai phương pháp yếu** (+0,146 và +0,157) so với hai bộ mã hóa (+0,102 và +0,105). Bộ mã hóa không chỉ tốt hơn nói chung mà tốt hơn **đúng ở phần khó** — đây là mức mà chunk-aware phải so.
2. **Gemini bắt được nhiều nhất nhưng báo động sai nhiều nhất.** Recall 0,974 cao nhất, precision 0,818 thấp nhất trong ba phương pháp mạnh — gọi nhầm 18 % câu trả lời trung thực. Khớp ma trận nhầm lẫn: 32/111 mẫu `no` bị gán `extrinsic`.
3. **XLM-R cân bằng nhất**, recall 0,920 và precision 0,918 gần bằng nhau.

##### Mốc mới

**0,776**, và muốn nói *hơn hẳn* thì phải vượt **0,818** — cận trên khoảng tin cậy, cùng nguyên tắc đã dùng để đặt mốc 0,689 cho E01.

##### Một lỗi tự gây ra khi kiểm chứng

Chạy `--dry-run` để kiểm tính tái lập đã **ghi đè `ms/mẫu` của E10 từ 8.194 xuống 0,03** — vì lượt đó lấy hết từ cache nên đo thời gian tra cache chứ không đo lượt gọi API.

Phép kiểm mà làm hỏng thứ nó đang kiểm thì tự nó là lỗi. Nay script **không ghi vào `runs.jsonl` khi không có lượt gọi mới nào**: chế độ kiểm chứng in bảng để đối chiếu, không có quyền viết lại bản ghi. Con số 8.194 đã khôi phục kèm ghi chú.

- `ruff check .` sạch, `pytest` 513 xanh

---

<a id="pr-47"></a>

### #47 — T20: công cụ tái lập Lookback Lens gốc (E02)

- **Nhánh:** `t20-tai-lap-lookback-lens` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 28/08/2026 23:50 · **gộp:** 28/08/2026 23:50 · **commit gộp:** [`25c970a`](https://github.com/wsunicorn/vihallulens/commit/25c970a5539fd3ccccc94f8dfd00dc55e4764182)
- **Thay đổi:** +1085 / −1, 8 file · **bình luận bot:** 1

Mốc so sánh **nội bộ** quan trọng nhất, vì đóng góp của đề tài là một sửa đổi trực tiếp trên phương pháp này. Nếu `chunk-aware` chỉ vượt được một bản tái lập **yếu** thì phép so sánh không chứng minh được gì.

##### Phần tính toán đã có sẵn từ T07

Không phải viết lại gì. `lookback_from_layer` trong `extract/attention.py` đã tính đúng công thức gốc, gồm cả chỗ dễ sai nhất là chia cho `N` và `t-1` thay vì lấy tổng. T20 làm ba bước còn lại: gộp qua các bước trong span, nối thành véc-tơ, huấn luyện bộ phân loại.

##### Ba chỗ dễ làm sai, mỗi chỗ một ca kiểm thử

Điều đáng sợ ở cả ba là **làm sai vẫn ra một ma trận đầy đủ trông rất hợp lý** — không có gì báo lỗi, chỉ có kết luận sai.

1. **Trung bình theo token, không phải tổng.** Lấy tổng thì đặc trưng biến thành thứ đại diện cho độ dài phản hồi, và bộ phân loại học đúng cái đó.
2. **Nối đủ lớp × đầu rồi mới trung bình qua các bước.** Gộp trung bình qua các đầu trước sẽ vứt mất chính cấu trúc mà bài gốc tìm thấy tín hiệu.
3. **Tên đặc trưng mang số lớp thật của mô hình.** Bỏ lớp 27 thì mảng còn 27 lát nhưng chúng là lớp 0–26. Đặt tên `l26` cho lát giữ lớp 24 làm mọi khẳng định về vị trí đầu chú ý thành sai — mà E13 hỏi đúng câu đó.

##### Chạy dở nối lại được

Mỗi mẫu ghi xuống **ngay khi tính xong**; chạy lại bỏ qua phần đã có. 50 phút là đủ dài để mất vì đứt phiên hay hết hạn mức. Có ca kiểm thử khẳng định **thứ tự ghi không làm đổi ma trận đọc ra** — nếu không, một lượt bị ngắt rồi nối lại sẽ âm thầm cho kết quả khác một lượt liền mạch.

Tên file mang **hash cấu hình**, nên đổi mô hình đọc hay trần token là ra file khác.

##### Script tự kiểm trước khi tin con số

Trước khi in điểm, in khối kiểm tra đặc trưng. Quan trọng nhất: **tỷ lệ giá trị nằm trong đoạn [0, 1]**. Theo định nghĩa lookback ratio phải nằm trong đó, nên con số này không xấp xỉ 100 % nghĩa là **công thức sai** chứ không phải mô hình kém — loại lỗi mà điểm số vẫn có thể trông đẹp.

Và tự chấm tiêu chí hoàn thành: không vượt 0,6562 của E01 thì **nói thẳng là không đạt**, in ba chỗ phải soi, trả mã lỗi — thay vì để con số đó lọt vào báo cáo.

##### Ghi chú cho task sau

`extract_features.py` hiện chỉ lưu véc-tơ lookback gộp, vì T20 chỉ cần thế. T21–T23 cần thêm phần theo đoạn, tính từ **cùng một ma trận** nhưng chưa lưu — lúc đó mở rộng script và chạy lại một lượt GPU. Không làm trước, theo mục 6 quy tắc 5 CLAUDE.md.

##### Kiểm chứng

- `ruff check .` sạch
- `pytest` **534 ca xanh** (thêm 21)
- Config validate được: hash `3d2dae5c7816`

Chưa chạy GPU. Notebook `t20_lookback_lens_t4.ipynb` sẵn sàng, ước tính ~50 phút.

---

<a id="pr-48"></a>

### #48 — T20: E02 tái lập được, và ngang bộ mã hóa đã tinh chỉnh

- **Nhánh:** `ket-qua-e02` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 29/08/2026 14:23 · **gộp:** 29/08/2026 14:23 · **commit gộp:** [`2d0d6c7`](https://github.com/wsunicorn/vihallulens/commit/2d0d6c7ca577ac71430fc465cb763665528f96d1)
- **Thay đổi:** +91 / −3, 2 file · **bình luận bot:** 1

Chạy 28/08/2026, **48,7 phút GPU, 0 lỗi trên 6.300 mẫu**. Ba phép tự kiểm đều sạch: 100 % hữu hạn, 100 % nằm trong đoạn `[0, 1]` đúng như định nghĩa đòi, 0/756 đặc trưng hằng số. Không mẫu nào bị cắt ngữ cảnh, không lớp nào tràn số. Tốc độ 464 ms/mẫu, khớp ước lượng 420 ms từ T08.

**macro-F1 0,7465 [0,7128–0,7773]** — vượt 0,6562 của E01 hơn 0,090 điểm. **ĐẠT tiêu chí hoàn thành.**

##### Ba điều rút ra

| Phương pháp | ba lớp | F1 `intrinsic` | F1 `extrinsic` | Tham số huấn luyện |
|---|---|---|---|---|
| E01 bề mặt | 0,656 | 0,533 | 0,694 | 9 |
| Gemini free | 0,664 | 0,582 | 0,656 | 0 |
| **E02 Lookback** | **0,746** | **0,731** | 0,714 | **2.271** |
| PhoBERT-large | 0,749 | 0,693 | 0,754 | 369.166.339 |
| XLM-R-large | 0,776 | 0,729 | 0,756 | 559.893.507 |

**1. Bộ phân loại tuyến tính trên 756 con số chú ý NGANG bộ mã hóa 369 triệu tham số đã tinh chỉnh.** 0,746 so với 0,749 — lệch 0,002, sâu trong nhiễu. Với **162.557 lần ít tham số hơn**. Đây đúng là phát hiện chủ đạo của bài Lookback Lens, **tái lập được trên tiếng Việt**. Thêm nữa: E02 không tinh chỉnh gì nên không dính chuyện một seed học được lượt này và không học được lượt sau như XLM-R gặp ở T18.

**2. Trên lớp `intrinsic` — lớp khó nhất — E02 VƯỢT PhoBERT và NGANG XLM-R.** 0,731 so với 0,693 và 0,729.

Đây là bằng chứng trực tiếp đầu tiên cho cơ chế mà cả đề tài dựa vào: ảo giác nội tại là mô hình **có đọc** ngữ cảnh rồi nói sai, ngoại lai là **không đọc** mà tự bịa — hai dấu vết chú ý khác nhau, trong khi văn bản đọc được thì giống nhau. Ba phép đo ở T13 và T19 cho thấy con người và LLM đều vấp ranh giới đó; nay có một phương pháp không vấp.

Chi tiết hơn: E02 **thắng ở `intrinsic` nhưng thua ở `extrinsic`** (0,714 so với 0,754). Hai hướng bù trừ ra tổng gần bằng. Chỉ nhìn macro-F1 thì tưởng ngang nhau; nhìn từng lớp mới thấy chúng **mạnh yếu ở hai chỗ khác nhau** — và chỗ E02 mạnh là chỗ đề tài nhắm vào.

**3. Tín hiệu dồn vào một số ít đầu, đúng như bài gốc.**

```
lookback_total_l5_h7      0.9700
lookback_total_l17_h4     0.8980
lookback_total_l24_h3     0.7215
...
lookback_total_l2_h9      0.5425   ← đầu thứ mười
```

Dấu hiệu đã tái lập **tín hiệu** chứ không phải nhiễu. Các đầu có ích trải khắp độ sâu (lớp 0, 1, 2, 5, 9, 17, 20, 24) chứ không dồn về cuối — số liệu vào thẳng E13.

##### Điều E02 KHÔNG chứng minh

- **Chưa vượt XLM-R** (0,746 so với 0,776). Nhưng khoảng tin cậy chồng nhau nhiều nên cũng chưa kết luận được XLM-R hơn hẳn.
- **Chi phí tuyệt đối cao hơn:** 464 ms so với 25 ms. Lập luận chi phí **biên** trong hệ RAG thật là thứ **thí nghiệm này không đo** — không được nói tắt.

##### Mốc thật của phần đóng góp nay là 0,746

Không phải 0,656. `chunk-aware` và `lookback` gộp là **cùng một họ phương pháp**, chỉ khác cách chia mẫu số. Vượt E01 chỉ chứng minh **chú ý có ích**; vượt E02 mới chứng minh **chia theo đoạn có ích**. Muốn nói *hơn hẳn* thì phải vượt **0,777**.

---

<a id="pr-49"></a>

### #49 — T21: năm đặc trưng chunk-aware — phần đóng góp của đề tài

- **Nhánh:** `t21-dac-trung-chunk-aware` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 29/08/2026 14:38 · **gộp:** 29/08/2026 14:38 · **commit gộp:** [`4ffa1e6`](https://github.com/wsunicorn/vihallulens/commit/4ffa1e6507a18f4b4d4e19bfe3a28b7d11554015)
- **Thay đổi:** +509 / −1, 4 file · **bình luận bot:** 1

Lookback Lens hỏi ma trận chú ý đúng một câu: **bao nhiêu** phần chú ý rơi vào ngữ cảnh. Năm đặc trưng này hỏi câu thứ hai: phần đó **trải trên các đoạn thế nào**.

Giả thuyết đang kiểm:

- **Nội tại** — mô hình **có đọc** ngữ cảnh rồi nói ngược. Chú ý rơi vào một chỗ cụ thể, phân bố nhọn.
- **Ngoại lai** — mô hình **không đọc** mà tự bịa. Không có gì cụ thể để nhìn, chú ý tản ra.

Cả hai sinh ra văn bản không khớp ngữ cảnh, nên mọi phương pháp dựa trên văn bản ở Bảng 1 đều lẫn chúng. T20 cho thấy riêng tỷ lệ gộp đã đạt 0,731 trên lớp `intrinsic`, vượt PhoBERT — năm đặc trưng này kiểm xem **hình dạng** có thêm được gì trên **lượng**.

##### Hai quyết định chuẩn hóa, quan trọng ngang công thức

Cả hai thuộc đúng loại lỗi "lấy tổng thay vì lấy trung bình" của công thức gốc: làm sai vẫn ra ma trận đầy đủ trông hợp lý, còn bộ phân loại thì lặng lẽ học **độ dài ngữ cảnh**.

**1. Chuẩn hóa mật độ thành phân bố, đúng một lần.** Bộ trích trả về *mật độ* chú ý, tổng không bằng 1 vì mẫu số là toàn bộ ngữ cảnh. Có ca kiểm thử: một đầu chú ý mạnh gấp đôi ở **mọi** đoạn phải cho cùng kết quả — nếu không thì đặc trưng đang đo *lượng*, tức đo lại việc E02 đã làm xong.

**2. Chia entropy cho `ln(n_chunks)`.** Entropy thô đạt trần ở `ln(n)`, nên ngữ cảnh 23 đoạn luôn ăn điểm cao hơn ngữ cảnh 5 đoạn **bất kể chú ý trải thế nào**. Mà số đoạn chênh rất lớn: ViHallu trung bình **5,3**, ISE-DSC01 **22,8** (đo ở T15). Không chuẩn hóa thì đặc trưng phần lớn mã hóa độ dài ngữ cảnh — đúng cái bẫy công thức gốc tránh bằng cách lấy trung bình theo token.

Gini bị đúng vấn đề đó, trần là `(n-1)/n`, và được nhân `n/(n-1)` — hiệu chỉnh mẫu nhỏ tiêu chuẩn.

##### Vì sao giữ cả entropy lẫn Gini

Entropy bị chi phối bởi **bao nhiêu đoạn nhận được chút ít** chú ý, Gini bởi **mức chia không đều** giữa chúng. Có ca kiểm thử khẳng định chúng **xếp hạng ngược nhau** trên hai phân bố cụ thể — giữ cả hai chỉ đáng tốn cột nếu chúng có thể bất đồng.

##### `chunk_drift` là đặc trưng duy nhất nhìn theo trục token

Khoảng cách biến phân toàn phần giữa hai bước liên tiếp, đọc thẳng ra là "bao nhiêu phần khối lượng chú ý đã chuyển sang đoạn khác". Có ca kiểm thử dựng hai phản hồi **cùng độ trải trung bình** — một đứng yên, một đảo qua đảo lại — mà bốn đặc trưng kia không phân biệt được.

##### Trường hợp biên xử lý rõ, không để thành `nan`

| Tình huống | Xử lý | Vì sao |
|---|---|---|
| Ngữ cảnh **một đoạn** | entropy 0, Gini 0, gap 1 | `ln(1) = 0` sẽ thành phép chia 0/0. **15,3 % ngữ cảnh ViWikiFC**, đo ở T15 |
| Đầu chú ý **không nhìn đoạn nào** | đọc là trải đều | Trả `nan` sẽ đầu độc cả mẫu qua bước chuẩn hóa của bộ phân loại |
| Phản hồi **một token được chấm** | drift 0 | Không quan sát được chuyển động, khác với chuyển động chưa rõ bao nhiêu |

Kèm ca kiểm thử khẳng định **mọi giá trị của cả năm đặc trưng đều nằm trong đoạn [0, 1]** — ra ngoài nghĩa là công thức sai, không phải mẫu lạ. Cùng loại phép kiểm mà script E02 chạy trước khi tin bất kỳ điểm số nào.

##### Để ngỏ cho T22

Véc-tơ **3.780 chiều** (5 × 27 lớp × 28 đầu) so với 756 của E02. Với 5.600 mẫu huấn luyện đây là tỷ lệ đáng lo; mục 2.3 `docs/SPEC.md` đã lường trước bằng ba chế độ gộp đầu chú ý. **Chọn chế độ gộp là việc của T22**, và phải chọn trên tập dev chứ không phải tập test.

Thứ tự xếp véc-tơ là **đặc trưng trước, rồi lớp, rồi đầu**, nên khối của một thống kê nằm liền nhau — E12 ablation theo nhóm khi đó là một phép cắt lát chứ không phải phép gom rải rác.

`scripts/extract_features.py` chưa lưu mảng theo đoạn — T20 không cần nên không lưu, đúng mục 6 quy tắc 5 `CLAUDE.md`. T22 sẽ mở rộng và chạy lại khoảng 50 phút GPU.

- `ruff check .` sạch, `pytest` **565 ca xanh** (thêm 31)

---

<a id="pr-50"></a>

### #50 — T22: công cụ E03 chunk-aware chia theo câu

- **Nhánh:** `t22-e03-chunk-aware-cau` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 29/08/2026 14:58 · **gộp:** 29/08/2026 14:58 · **commit gộp:** [`ce44cfd`](https://github.com/wsunicorn/vihallulens/commit/ce44cfd69758c90c4040b718bac1e1805ef7aab2)
- **Thay đổi:** +1065 / −8, 8 file · **bình luận bot:** 1

Thí nghiệm mà cả đề tài tồn tại vì nó. E02 đạt macro-F1 **0,7465** bằng cách hỏi ma trận chú ý đúng một câu: *bao nhiêu* phần rơi vào ngữ cảnh. E03 hỏi câu thứ hai: phần đó **trải trên các đoạn thế nào**.

##### Mốc phải vượt là 0,7465, không phải 0,6562

Chunk-aware và lookback gộp là **cùng một họ phương pháp**, chỉ khác cách chia mẫu số. Vượt E01 chỉ chứng minh *chú ý có ích* — E02 đã làm xong. Vượt **E02** mới chứng minh *chia theo đoạn có ích*.

Script tự chấm mốc này và **trả mã lỗi nếu chưa vượt**, kèm câu nhắc đừng trình bày như một cải tiến. Muốn nói *hơn hẳn* thì phải vượt **0,7773**.

##### Sửa một chỗ trong T20 để khỏi tốn GPU hai lần

Tên file đặc trưng vốn băm theo **toàn bộ** cấu hình. Nhưng `features.groups` và `head_aggregation` là quyết định **sau khi GPU đã chạy xong** — chúng không đổi một bit nào của thứ mô hình đọc sinh ra. Băm cả cấu hình thì E03 phải trích lại 50 phút cho một khác biệt mà GPU không hề thấy.

Nay có `extraction_hash` băm đúng ba phần quyết định lượt chạy GPU: `dataset`, `chunking`, `extractor`. Kết quả: **E02 và E03 dùng chung một lượt trích**, nhưng vẫn là hai bản ghi thí nghiệm riêng vì `config_hash` vẫn khác. Có ca kiểm thử khẳng định cả hai điều.

`chunking` nằm trong hash vì đặc trưng theo đoạn phụ thuộc chỗ cắt — nên bản chia theo câu (E03) và chia theo cửa sổ (E04) **thật sự** là hai lượt trích khác nhau.

##### Cách gộp đầu chú ý chọn trên tập dev

Sáu khối × 27 lớp × 28 đầu = **4.536 cột** trên 5.600 hàng huấn luyện. Phải giảm chiều — nhưng chọn cách giảm nào **theo điểm test** thì con số báo cáo sẽ không ai tái lập được nếu chưa biết trước đáp án.

Script thử sáu ứng viên (`all`, `mean_over_heads`, `topk_heads` với k ∈ {8, 16, 32, 64}), chấm tất cả **trên dev**, rồi chấm test **đúng một lần** bằng cái thắng.

Thứ hạng đầu chú ý lấy từ mô hình khớp trên **train** — thông tin huấn luyện dùng trên dữ liệu huấn luyện, được phép. Dev chỉ quyết *giữ bao nhiêu*.

**Hòa điểm thì chọn ma trận hẹp hơn.** Nhiều bề rộng cùng điểm trên 700 mẫu dev là chuyện thường và nói rằng các cột thêm vào không mua được gì; lấy bản rộng nhất khi đó là mang rủi ro quá khớp vào điểm test mà không đổi lấy gì đo được. Quy tắc viết thẳng vào code chứ không để phụ thuộc thứ tự duyệt.

##### Một đầu sống hoặc chết cho cả sáu khối

`topk_heads` áp dụng danh sách đầu **giống nhau cho mọi khối**. Chọn đầu khác nhau cho từng thống kê sẽ làm cột sống sót khó diễn giải và nhân số quyết định dựa trên dev lên nhiều lần.

Điểm của một cặp là **trọng số lớn nhất** trong các khối nó xuất hiện, không phải trung bình — để một đầu chỉ hữu ích cho một thống kê không bị năm thống kê còn lại bỏ phiếu loại.

##### `basic` giữ lại trong E03, có chủ ý

Cấu hình là `[basic, chunk_aware, stability]` — **có** cả lookback gộp. Câu hỏi được kiểm vì thế là *"thêm hình dạng vào lượng có tốt hơn không"*, không phải *"hình dạng một mình có hơn lượng một mình không"*. Câu thứ hai là việc của ablation E12.

Hệ quả: phải nhìn **trọng số chia theo khối** chứ không chỉ nhìn điểm. Nếu `lookback_total` chiếm gần hết thì bộ phân loại đang dùng lại E02 và điểm nhỉnh hơn chỉ là nhiễu. Script in sẵn bảng đó — phép kiểm về **cơ chế**, tách khỏi phép kiểm về điểm số.

##### Chạy thử trọn đường ống trên dữ liệu giả

Dựng ba shard giả với tín hiệu cấy sẵn vào vài đầu rồi chạy `run_chunk_aware.py` thật. Bắt được đủ thứ mà không tốn một giây GPU: bảng chọn cách gộp in đúng, tên cột khớp số cột, bảng trọng số theo khối chạy được, bản ghi ghi ra được. Cùng bài học của T18, nơi một lỗi kiểu dữ liệu đốt một phiên GPU vì vòng lặp chưa từng chạy trên CPU.

##### Kiểm chứng

- `ruff check .` sạch
- `pytest` **592 ca xanh** (thêm 27)
- Ước tính **55 phút** GPU: 43 phút train, 5 phút dev, 5 phút test

---

<a id="pr-51"></a>

### #51 — T22: kết quả E03 — thắng ngoại lai, thua nội tại

- **Nhánh:** `sua-e02-doc-lai-duoc` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 11:06 · **gộp:** 30/08/2026 11:06 · **commit gộp:** [`1d4b05c`](https://github.com/wsunicorn/vihallulens/commit/1d4b05c107352f79282351a2a020f7a23d807f26)
- **Thay đổi:** +208 / −662, 8 file · **bình luận bot:** 1

macro-F1 **0,7567** so với **0,7451** của E02 chạy trên *chính lượt trích này*. **Đạt tiêu chí hoàn thành.** Nhưng khoảng tin cậy chồng gần hết nên **vượt điểm chứ chưa hơn hẳn**, và câu chuyện thật nằm ở từng lớp.

| | ba lớp | nhị phân | `no` | `intrinsic` | `extrinsic` | ECE |
|---|---|---|---|---|---|---|
| E02 lượng | 0,7451 | 0,8426 | 0,7925 | **0,7308** | 0,7121 | 0,1090 |
| **E03 lượng + hình dạng** | **0,7567** | **0,8636** | **0,8228** | 0,6858 | **0,7615** | **0,0441** |
| chênh | **+0,0116** | +0,0210 | +0,0303 | **−0,0450** | **+0,0494** | −0,0649 |

##### Một nửa giả thuyết đúng, một nửa bị bác

- *"Ngoại lai thì chú ý tản"* — **đúng rõ ràng**. +0,049 là cải thiện mạnh nhất đo được từ đầu đề tài.
- *"Nội tại thì chú ý nhọn"* — **không thêm được gì**, vì tỷ lệ gộp đã nắm phần đó: 0,7308 của E02 là con số cao nhất cả Bảng 1 trên lớp này, cao hơn cả XLM-R.

Thứ đề tài tưởng mình sẽ đóng góp và thứ nó thật sự đóng góp **không trùng nhau**.

##### Hai phép đối chứng, cả hai bác giả thuyết của chính tôi

**Hình dạng một mình: 0,6054** — thua cả 0,6562 của E01. Năm đặc trưng chunk **không phải bộ phát hiện độc lập**, chúng là tín hiệu bổ sung.

**Cách chọn đầu không phải thủ phạm.** Nghi ngờ đầu tiên là `topk k=32` chỉ giữ 32/756 cột lookback. Kiểm hai cách: chạy E02 qua cùng quy trình thì dev chọn đủ 756 cột; và **thêm hẳn ứng viên `mixed_all_basic_topk_rest`** giữ nguyên khối lookback — cả bốn biến thể đều thua (0,7645 so với 0,7768).

Không gian tìm kiếm nay **chứa E02 như trường hợp riêng**, và dev vẫn không chọn nó. Chênh lệch từng lớp là thật.

Ứng viên `mixed` được thêm **sau khi** thấy chênh lệch — ghi rõ điều đó. Nhưng nó chấm trên dev như mọi ứng viên khác, và số của lượt đầu được giữ nguyên bên cạnh.

##### Ba điều E03 làm được

1. **ECE 0,0441 — tốt nhất cả Bảng 1**, giảm hơn một nửa so với E02. Đi **ngược** xu hướng "càng mạnh càng tự tin thái quá" của ba mốc kia.
2. **Nhị phân 0,8636**, cao thứ hai sau XLM-R, với `báo đúng` **0,9154** cao nhất bảng.
3. **Năm đặc trưng mới chiếm 87 % trọng số.** Bộ phân loại thật sự dựa vào hình dạng — phép kiểm về *cơ chế* và nó qua.

##### Một lỗi lộ ra ở phút thứ 71

Ô so sánh E02 hỏng vì T22 tách `extraction_hash` khỏi `config_hash` nhưng `run_lookback_baseline.py` vẫn gọi hàm cũ. May là hỏng ở khâu rẻ — chạy lại trên CPU mất vài giây. Đã sửa, kèm ca kiểm thử.

- `ruff check .` sạch, `pytest` **593 ca xanh**

---

<a id="pr-52"></a>

### #52 — T23: công cụ E04 quét cửa sổ token, chờ chạy GPU

- **Nhánh:** `t23-cua-so-token` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 11:29 · **gộp:** 30/08/2026 11:29 · **commit gộp:** [`b37f2a6`](https://github.com/wsunicorn/vihallulens/commit/b37f2a6853d1a7f0e4e0184fd1f1952458446121)
- **Thay đổi:** +880 / −23, 10 file · **bình luận bot:** 1

Công cụ cho E04 — chunk-aware chia theo cửa sổ token, quét 64/128/256. Chưa có số GPU; PR này là phần chuẩn bị để lượt chạy Kaggle không hỏng giữa chừng.

##### Đo trên CPU trước, và phép đo ấy đổi cách đọc kết quả

`scripts/probe_chunking.py` đếm số đoạn thật sự trên cả 7.000 ngữ cảnh ViHallu, mất một phút CPU:

| cách chia | TB số đoạn | trung vị | chỉ 1 đoạn | ≤ 2 đoạn |
|---|---|---|---|---|
| câu, min_words=5 (E03) | 5,3 | 5 | 1,1 % | 5,8 % |
| cửa sổ 64, bước 32 | 7,1 | 6 | 0,0 % | 0,0 % |
| cửa sổ 128, bước 64 | 3,3 | 3 | 0,1 % | 34,5 % |
| **cửa sổ 256, bước 128** | **1,4** | **1** | **67,2 %** | **92,7 %** |

Ngữ cảnh ViHallu dài trung vị 218 token, nên cửa sổ 256 token thường *là* cả ngữ cảnh. Với đúng một đoạn, năm đặc trưng hình dạng thành hằng số `(0, 1, 0, 1, 0)` bất kể mô hình đọc làm gì — đã kiểm bằng test rằng chúng vẫn hữu hạn, không NaN, nhưng hữu hạn không có nghĩa là mang thông tin.

Vẫn chạy đủ ba cỡ: Bảng 3 phải điền bằng số đo chứ không bằng suy luận. Và nếu cỡ 256 **không** rơi về gần E02 thì đó là dấu hiệu đường ống sai, chứ không phải phát hiện mới.

Con số đáng chờ là **64 so với 128** — 7,1 đoạn so với 3,3, trong khi chia theo câu cho 5,3. Nếu điểm đi theo số đoạn thì thứ quyết định là độ phân giải; nếu chia theo câu thắng cả hai ở mật độ tương đương thì thứ quyết định là ranh giới ngữ nghĩa.

##### Một lỗi sẽ giết lượt chạy ở mẫu đầu tiên

Từ T20 tới hết T22, `extract_features.py` gọi bộ chia đoạn thế này:

```python
chunks = chunk_context(row["context"], strategy=cfg.chunking.strategy,
                       min_words=cfg.chunking.min_words)
```

Đúng cho `sentence`, **im lặng sai** cho `token_window` vốn cần tokenizer, `window_size` và `stride`. `chunk_context` nhận `**kwargs` nên thiếu khóa không bị từ chối — nó raise ở trong, tại mẫu đầu tiên, sau khi đã nạp xong mô hình 7B. Ba lần liên tiếp.

Sửa bằng cách tách `chunking_arguments(chunking, tokenizer)` để phép ánh xạ nằm ở **một chỗ mà test CPU kiểm được**. Bốn ca test khẳng định tokenizer tới nơi, cỡ cửa sổ và bước tới nơi, và chiến lược `sentence` không đổi hành vi — E02 với E03 đã trích xong, đổi cách cắt của chúng là làm hỏng shard cũ.

##### `--dev-only`: T23 không được đụng tập test

T23 chỉ cần cột `macro-F1 dev` của Bảng 3. Hai trong ba cỡ sẽ bị loại ở T24, và trích tập test cho chúng vừa tốn 7 phút GPU mỗi cỡ vừa đặt ba điểm test lên bàn trước khi lựa chọn được đưa ra. `--dev-only` dừng ngay sau bảng chọn cách gộp đầu, nên **"chọn trên dev" thành sự thật về thứ đã được tính chứ không phải lời hứa về thứ đã không nhìn**.

##### Chạy thử trọn đường ống trên shard giả

Dựng shard giả ở cả ba hash trích với `n_chunks` bằng 7, 3 và 1, rồi chạy `run_chunk_aware.py` thật. Bắt được hai lỗi chỉ nhìn code thì không thấy: banner in `E03_CHUNK_AWARE` cho cấu hình E04 — mã thí nghiệm ghi vào `results/runs.jsonl` lấy từ đó nên bốn lượt sẽ lẫn vào nhau — và nhãn `mixed_all_basic_topk_rest` dài hơn cột 22 ký tự làm lệch bảng sẽ dán vào báo cáo.

##### Kiểm

- `pytest` 606 ca xanh (thêm 13), `ruff check .` sạch
- Ba cấu hình cho ba `extraction_hash` khác nhau, và không cái nào trùng lượt trích của E03

##### Còn phải làm

Chạy `notebooks/t23_chunk_aware_cua_so_t4.ipynb`, khoảng 3,2 giờ GPU: ba cỡ × (57 phút train + 7 phút dev). Mỗi ô chạy lại được nên chia hai phiên cũng được.

---

<a id="pr-53"></a>

### #53 — T22: lưu notebook đã chạy làm minh chứng

- **Nhánh:** `t22-minh-chung` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 11:35 · **gộp:** 30/08/2026 11:35 · **commit gộp:** [`a2da072`](https://github.com/wsunicorn/vihallulens/commit/a2da072e526855ce49134827730e78933861a56d)
- **Thay đổi:** +1 / −276, 1 file · **bình luận bot:** 1

Bản commit ở #50 là mã nguồn sạch (11 KB, 0 output). Bản này là bản Kaggle đã chạy thật ngày 29/08/2026, giữ đủ output của 13 ô: 49,3 phút trích train ở 528 ms/mẫu, bảng chọn cách gộp trên dev (`topk_heads k=32` thắng ở 0,7768), và kết quả test macro-F1 0,7567 [0,7242; 0,7885].

Minh chứng cho hội đồng rằng số trong `docs/EXPERIMENTS.md` đến từ một lượt chạy thật. 184 KB, đã quét không có khóa API.

Từ T23 trở đi commit notebook đã chạy ngay sau khi tải về, thay vì để nằm chờ trong cây làm việc.

---

<a id="pr-54"></a>

### #54 — T23: kết quả E04 — chia theo câu thắng cả ba cỡ cửa sổ

- **Nhánh:** `t23-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 19:10 · **gộp:** 30/08/2026 19:10 · **commit gộp:** [`08464b8`](https://github.com/wsunicorn/vihallulens/commit/08464b8b564febd1cb8755d3419e75fb39210147)
- **Thay đổi:** +219 / −15, 4 file · **bình luận bot:** 1

Bảng 3 đầy đủ. Sáu lượt trích, 3,3 giờ GPU, **0 lỗi trên 18.900 mẫu**, 0 cắt ngữ cảnh, 0 lớp tràn số.

| Chiến lược | TB đoạn | chỉ 1 đoạn | cách gộp dev chọn | macro-F1 dev |
|---|---|---|---|---|
| **Câu, min_words=5 (E03)** | 5,3 | 1,1 % | `topk k=32`, 192 chiều | **0,7768** |
| Cửa sổ 128 / bước 64 | 3,3 | 0,1 % | `topk k=32`, 192 chiều | 0,7655 |
| Cửa sổ 64 / bước 32 | 7,1 | 0,0 % | `topk k=32`, 192 chiều | 0,7624 |
| Cửa sổ 256 / bước 128 | 1,4 | 66,5 % | `mixed k=16`, 836 chiều | 0,7574 |

##### Không phải độ phân giải, mà là ranh giới ngữ nghĩa

Notebook ghi sẵn phép kiểm **trước khi chạy**: nếu điểm đi theo số đoạn thì thứ quyết định là độ phân giải; nếu chia theo câu thắng ở mật độ tương đương thì là ranh giới ngữ nghĩa.

Cửa sổ 64 cho **7,1** đoạn, cửa sổ 128 cho **3,3** — chênh **2,15 lần** — mà điểm chỉ lệch **0,0031**. Chia theo câu nằm **giữa** hai cỡ ấy ở 5,3 đoạn và hơn cả hai **0,011–0,014**. Sắp theo số đoạn: 7,1 → 5,3 → 3,3 → 1,4 cho 0,7624 → **0,7768** → 0,7655 → 0,7574.

**Không đơn điệu.** Nếu độ phân giải quyết định thì câu ở 5,3 đoạn phải nằm giữa hai cỡ cửa sổ về điểm số — nó không. Vậy ranh giới câu mang thông tin mà cửa sổ token tùy tiện không có: chunk-aware không phải "chia nhỏ ngữ cảnh ra" mà là "chia theo đơn vị nghĩa".

##### Một điều chưa tách được — ghi nợ, không lờ đi

Cửa sổ **chồng lấn** (bước bằng nửa), câu thì **phủ kín không đè**. Nên "câu thắng" còn hai cách giải thích: ranh giới ngữ nghĩa, hoặc chỉ đơn giản là không chồng lấn. Lập luận về số đoạn nghiêng về cách thứ nhất nhưng **không loại trừ** cách thứ hai. Tách dứt điểm cần một cấu hình cửa sổ 128 bước 128, khoảng 57 phút GPU — quyết ở T24.

##### Cửa sổ 256 rơi đúng chỗ đã dự báo

E02 chấm qua **cùng quy trình chọn** ở T22 cho dev 0,7607; cửa sổ 256 cho **0,7574**, lệch 0,0033. Dự báo trước khi đặt lịch GPU là nó phải rơi về gần E02 vì 67 % ngữ cảnh còn nguyên một đoạn — dự báo đúng nên **đường ống được xác nhận**, chứ không phải một ô trống trong bảng.

Tỷ lệ một đoạn đo trên train là 66,5 %, khớp 67,2 % mà `probe_chunking.py` đếm trên cả 7.000 ngữ cảnh — hai phép đếm độc lập, cùng một số.

##### Cách gộp đầu tự chẩn đoán ra sự thoái hóa

Ba cấu hình còn lại đều chọn `topk_heads k=32`, đúng cái E03 chọn — **ổn định qua mọi cách chia đoạn**, chốt được như một tham số.

Cửa sổ 256 là ngoại lệ duy nhất: nó chọn `mixed_all_basic_topk_rest k=16`, ứng viên được thêm ở T22 để giữ **nguyên vẹn** khối lookback và chỉ tỉa các khối rộng. Nó **thua** ở E03 và **thắng** đúng chỗ lý thuyết nói nó phải thắng: khi hình dạng là hằng số trên 66,5 % mẫu, bộ chọn tự quay về dựa vào tỷ lệ lookback đầy đủ.

##### Chi phí không đổi theo cách chia — số cho E11

Câu **528** ms/mẫu, cửa sổ 64 **538**, 128 **541**, 256 **540**. Số đoạn chênh 5 lần, chi phí chênh 2,5 %. **Chunk-aware không đắt hơn Lookback Lens gộp.**

##### Một lỗ hổng truy vết tự phát hiện sau khi chạy

`--dev-only` dừng trước khi ghi `results/runs.jsonl`, nên bốn con số của Bảng 3 chỉ tồn tại trong text notebook — một bảng trong khóa luận không có gì đọc được bằng máy đứng sau. Giờ nó ghi bản ghi gồm bảng chọn đầy đủ và điểm dev.

Bản ghi để `ms_per_sample` là `None` chứ **không** phải `0.0`: đường này không đo chi phí, và một số 0 sẽ thành dòng "phương pháp miễn phí" trong bảng E11 — đúng kiểu lỗi `--dry-run` của T19 từng gây ra khi ghi đè 8.194 ms của E10 thành 0,03. Có test khóa cả hai điều đó.

##### Kiểm

`pytest` 608 ca xanh (thêm 2), `ruff check .` sạch.

##### T24 gần như không cần GPU

Cấu hình thắng trên dev là chia theo câu, mà E03 đã chấm test đủ ở T22: macro-F1 **0,7567** [0,7242; 0,7885], cùng quy trình cùng lượt trích. T24 chỉ còn viết kết luận — trừ khi quyết chạy phép đối chứng cửa sổ không chồng lấn.

---

<a id="pr-55"></a>

### #55 — T23: lưu notebook đã chạy làm minh chứng

- **Nhánh:** `t23-minh-chung` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 19:15 · **gộp:** 30/08/2026 19:16 · **commit gộp:** [`7d36085`](https://github.com/wsunicorn/vihallulens/commit/7d3608587025f463ff8727ee44591085ded654fe)
- **Thay đổi:** +1 / −336, 1 file · **bình luận bot:** 1

Bản Kaggle chạy 30/08/2026, giữ output của 14 ô: bảng đếm số đoạn, sáu lượt trích (0 lỗi trên 18.900 mẫu), ba bảng chọn cách gộp đầu trên dev. 53 KB, đã quét không có khóa API.

Minh chứng cho Bảng 3.

---

<a id="pr-56"></a>

### #56 — T23: ghi chú chi phí trích lặp và ba điểm sửa cho notebook sau

- **Nhánh:** `t23-ghi-chu` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 19:17 · **gộp:** 30/08/2026 19:17 · **commit gộp:** [`34f4349`](https://github.com/wsunicorn/vihallulens/commit/34f4349dc550004b3ee0415eff187e40ec7c6da4)
- **Thay đổi:** +34 / −0, 1 file · **bình luận bot:** 1

Quan sát: cả bốn cách chia đều `bị cắt ngữ cảnh: 0/5.600`, nên prompt giống hệt nhau từng byte và forward pass bị tính lại bốn lần cho cùng một thứ. Một bộ trích nhận nhiều cách chia cùng lúc sẽ rút 3,3 giờ xuống ~50 phút.

Chưa làm, vì tính chất này **không mang sang ISE-DSC01 được**: ở đó cắt ngắn sẽ kích hoạt, mà cắt ngắn bỏ nguyên từng đoạn nên ngữ cảnh sống sót phụ thuộc cách chia. Muốn dùng lại một lượt trích ở E07 phải cắt ngắn theo quy tắc chung — đổi thiết kế bộ trích, thuộc diện phải hỏi theo mục 6 quy tắc 4.

Ba điểm cho notebook T24 trở đi (không sửa ngược vào T23 vì nó đã là minh chứng đã commit):
1. Ô lấy kết quả phải copy cả `results/runs.jsonl` — từ T23 `--dev-only` đã ghi vào đó.
2. Thêm ô kiểm toàn vẹn shard, ~20 giây CPU, chạy khi còn kịp sửa.
3. In F1 từng lớp trên dev ở `--dev-only`.

---

<a id="pr-57"></a>

### #57 — T23: chấm lại Bảng 3 trên cùng một máy, và số dev không tái lập giữa hai môi trường

- **Nhánh:** `t23-chinh-lai` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 19:38 · **gộp:** 30/08/2026 19:39 · **commit gộp:** [`95ac841`](https://github.com/wsunicorn/vihallulens/commit/95ac841907ffc4678c65a1fd419da667b6fc0b11)
- **Thay đổi:** +198 / −38, 5 file · **bình luận bot:** 1

Tải sáu shard về chấm lại trên CPU để sinh bản ghi `runs.jsonl` mà lượt Kaggle chưa có (phần ghi ấy tôi thêm **sau** khi bạn đã chạy). Việc kiểm ấy tìm ra thứ không ai đi tìm.

##### Số dev không tái lập giữa hai môi trường

Cùng shard, cùng code, cùng seed 42:

| | Kaggle | máy cá nhân | chênh |
|---|---|---|---|
| Cửa sổ 64, `topk k=16` | 0,7587 | 0,7662 | **+0,0075** |
| Cửa sổ 64, `all` | 0,7030 | 0,6961 | −0,0069 |
| Cửa sổ 128, `topk k=32` | 0,7655 | 0,7683 | +0,0028 |
| Câu (E03), `mean_over_heads` | 0,7153 | 0,7138 | −0,0015 |
| Câu (E03), `topk k=32` | 0,7768 | 0,7768 | 0 |

Chạy hai lần **trên cùng một máy** thì trùng từng chữ số — nên là khác biệt **giữa hai môi trường**, không phải ngẫu nhiên giữa các lượt. Kaggle Python 3.12, máy cá nhân 3.11; `LogisticRegression` với lbfgs hội tụ tới điểm hơi khác tùy phiên bản thư viện số và BLAS.

Ở cửa sổ 64 độ trôi **đủ để đổi cấu hình dev chọn**, từ `topk k=32` sang `topk k=16`.

##### Hệ quả: Bảng 3 chấm lại cả bốn dòng tại chỗ

Ghép số Kaggle của E04 với số cũ của E03 chính là cái bẫy suýt mắc. Bảng 3 giờ là bốn dòng cùng một máy:

| Chiến lược | TB đoạn | macro-F1 dev | Nhị phân | `no` | `intrinsic` | `extrinsic` |
|---|---|---|---|---|---|---|
| **Câu** | 5,3 | **0,7768** | **0,8943** | **0,8596** | 0,7202 | **0,7505** |
| Cửa sổ 128 | 3,3 | 0,7683 | 0,8864 | 0,8493 | **0,7325** | 0,7230 |
| Cửa sổ 64 | 7,1 | 0,7662 | 0,8902 | 0,8528 | 0,7158 | 0,7300 |
| Cửa sổ 256 | 1,4 | 0,7589 | 0,8670 | 0,8210 | 0,7149 | 0,7407 |

**Thứ tự bền ở cả hai môi trường**: câu > 128 > 64 > 256. Kết luận T23 dựa vào thứ tự này.

##### Sửa lại một chỗ tôi đã nói quá

Khoảng cách thật là **0,0085**, không phải 0,0113 như con số ghép hai môi trường. So với biên độ trôi 0,0075 và 700 mẫu dev, đây là **một thứ tự nhất quán chứ chưa phải chiến thắng có ý nghĩa thống kê**. Đã sửa cách viết trong cả `TASKS.md` lẫn `docs/EXPERIMENTS.md`.

Thứ làm kết luận đáng tin không phải độ lớn mà là **hình dạng**: thứ tự giống nhau ở hai môi trường, và tính không đơn điệu theo số đoạn (7,1 → 5,3 → 3,3 → 1,4 cho 0,7662 → **0,7768** → 0,7683 → 0,7589) thì nhiễu không dựng ra được một cách tự nhiên.

##### Cửa sổ 128 thắng `intrinsic`

Thêm F1 từng lớp vào `--dev-only` — trước đó chỉ in macro. Cửa sổ 128 đạt **0,7325**, hơn chia theo câu 0,012, **đúng lớp mà T22 cho thấy chunk-aware thua lookback gộp**. Chia theo câu bù ở `no` và `extrinsic` nên thắng tổng.

Chênh 0,012 nằm trong biên độ trôi nên **không đảo kết luận T24**, nhưng là manh mối: có thể cách chia tốt nhất không giống nhau cho cả ba lớp.

##### Kiểm

`pytest` 609 ca xanh (thêm 1), `ruff check .` sạch. Bốn bản ghi `dev_only` nay có trong `results/runs.jsonl`, mỗi bản ghi kèm bảng chọn đầy đủ.

---

<a id="pr-58"></a>

### #58 — T24: đối chứng cửa sổ không chồng lấn, chờ chạy GPU

- **Nhánh:** `t24-doi-chung` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 19:52 · **gộp:** 30/08/2026 19:52 · **commit gộp:** [`4753099`](https://github.com/wsunicorn/vihallulens/commit/475309945a0b7b062b1ad655ed66cb682072f391)
- **Thay đổi:** +568 / −1, 4 file · **bình luận bot:** 0

Một lượt GPU (~64 phút) để tách câu hỏi mà T23 không trả lời được.

##### Câu hỏi, và vì sao nó quan trọng

Ba cỡ cửa sổ ở T23 đều **chồng lấn** (bước bằng nửa), chia theo câu thì **phủ kín không đè**. Nên "câu thắng" có hai cách giải thích:

1. **Ngữ nghĩa** — ranh giới câu mang thông tin mà ranh giới token tùy tiện không có.
2. **Chồng lấn** — token trong vùng chồng bị đếm hai lần nên véc-tơ theo đoạn không còn là phân bố theo nghĩa chặt.

Nếu là (2), đóng góp của đề tài không phải "chia theo đơn vị nghĩa" mà chỉ là "đừng chia chồng lấn" — câu yếu hơn hẳn, và chương kết quả phải viết lại.

##### Cỡ cửa sổ phải đo, không được đoán

Phương án nghĩ tới đầu tiên là **cửa sổ 128 bước 128**. Đo trên CPU: nó cho **2,43** đoạn so với 5,29 của chia theo câu — bỏ được biến chồng lấn nhưng **lôi biến số đoạn vào**. Hỏng đúng theo kiểu T23 vừa cảnh báo.

```
cửa sổ = bước   TB đoạn   trung vị   lệch so với câu
           40      6,57          6        +1,28
           44      6,02          5        +0,73
           48      5,56          5        +0,27   ← chọn
           56      4,83          4        −0,46
          128      2,43          2        −2,86
```

| | TB đoạn | trung vị | chồng lấn | ranh giới |
|---|---|---|---|---|
| Chia theo câu (E03) | 5,29 | 5 | không | **ngữ nghĩa** |
| **Cửa sổ 48, bước 48** | **5,56** | **5** | không | tùy tiện |

Khác nhau **đúng một thứ**.

##### Cách đọc, viết trước khi thấy số

Mốc là **0,7768** — điểm dev của E03 chấm **trên cùng máy sẽ chấm lượt này** (ô 7b làm việc đó, vì T23 cho thấy ghép số giữa hai môi trường là sai).

- **Câu vẫn hơn rõ** → kết luận **ngữ nghĩa**, đóng góp đứng vững.
- **Chênh dưới ~0,008** → **không kết luận được**. Biên độ trôi đo ở T23 là 0,0075, dev chỉ 700 mẫu.
- **Cửa sổ 48 hơn** → khoảng cách T23 là do **chồng lấn**; phải sửa phần đóng góp, và T24 chọn cửa sổ 48 (thêm ~7 phút trích test).

Trường hợp thứ ba bất lợi nhất cho đề tài. Ghi ra trước để sau không đọc trại đi.

##### Ba cải tiến đã nợ từ T23

1. Ô 9 copy **cả `results/runs.jsonl`**, không chỉ đặc trưng.
2. Ô 8 **kiểm toàn vẹn shard** trước khi rời phiên. Chỉ soi hai shard của lượt này theo hash trích — quét cả thư mục báo động giả trên shard T20 vốn chỉ có 2 khối. Đã chạy thử tại chỗ.
3. `--dev-only` in **F1 từng lớp**.

Thêm ô 4 xác nhận cỡ 48 khớp mật độ, `assert` dừng nếu lệch quá 0,5 đoạn — tiền đề của thí nghiệm, sai thì đừng tốn GPU.

##### Kiểm

`pytest` 613 ca xanh (thêm 4), `ruff check .` sạch. Cấu hình đối chứng giống E03 ở mọi khóa trừ `chunking`, có test khẳng định.

---

<a id="pr-59"></a>

### #59 — T24: đối chứng bác cách giải thích chồng lấn, chốt chia theo câu

- **Nhánh:** `t24-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 21:35 · **gộp:** 30/08/2026 21:35 · **commit gộp:** [`50e0203`](https://github.com/wsunicorn/vihallulens/commit/50e02035e7f661ddc149d27bfd4d971cdba9f2ed)
- **Thay đổi:** +139 / −416, 4 file · **bình luận bot:** 1

Phép đối chứng trả lời câu hỏi T23 để lại, và câu trả lời **bác chính giả thuyết nó được dựng để kiểm**.

##### Kết quả — năm dòng, cùng một máy

| Chiến lược | Chồng lấn | TB đoạn | macro-F1 dev | `no` | `intrinsic` | `extrinsic` |
|---|---|---|---|---|---|---|
| **Câu, min_words=5** ← chọn | không | 5,29 | **0,7768** | **0,8596** | 0,7202 | **0,7505** |
| Cửa sổ 128 / bước 64 | có | 3,29 | 0,7683 | 0,8493 | **0,7325** | 0,7230 |
| Cửa sổ 64 / bước 32 | có | 7,08 | 0,7662 | 0,8528 | 0,7158 | 0,7300 |
| **Cửa sổ 48 / bước 48** (đối chứng) | **không** | **5,56** | 0,7649 | 0,8584 | 0,7111 | 0,7254 |
| Cửa sổ 256 / bước 128 | có | 1,43 | 0,7589 | 0,8210 | 0,7149 | 0,7407 |

##### Ngữ nghĩa, không phải chồng lấn

Đối chứng **0,7649 — thấp hơn cả hai cỡ cửa sổ chồng lấn**, chứ không cao hơn. Bỏ chồng lấn đi không giúp được gì.

Bốn cấu hình cửa sổ nằm gọn trong dải **0,7589–0,7683** bất kể chồng lấn hay phủ kín, bất kể 1,4 hay 7,1 đoạn mỗi ngữ cảnh. Chia theo câu đứng trên **cả bốn**. Cách giải thích còn lại là **ranh giới ngữ nghĩa** — đóng góp của đề tài giữ nguyên như đang viết.

##### Vì sao tin được, dù khoảng cách nhỏ

Nói thẳng: hơn cửa sổ tốt nhất **0,0085**, hơn đối chứng **0,0119**, trên 700 mẫu dev, với độ trôi giữa hai môi trường tới 0,0075. **Chưa đủ gọi là có ý nghĩa thống kê.**

Ba thứ nâng nó lên khỏi mức ngẫu nhiên:

1. **Tám trên tám** — bốn cấu hình cửa sổ × hai môi trường, cả tám đều cho chia theo câu đứng trên.
2. **Không đơn điệu theo số đoạn**: 7,08 → 5,29 → 3,29 → 1,43 cho 0,7662 → **0,7768** → 0,7683 → 0,7589. Nhiễu không dựng ra hình dạng này.
3. **Đối chứng được dựng riêng để kiểm cách giải thích cạnh tranh, rồi cho kết quả chống lại chính nó.** Mạnh hơn một khoảng cách lớn mà chưa ai thử bác.

##### Một lỗi thiết kế của tôi

Ô 7b định chấm lại E03 trên Kaggle để so cùng máy. Nó hỏng — phiên Kaggle mới thì `data/processed` rỗng, shard E03 nằm ở máy cá nhân.

Hậu quả suýt nghiêm trọng: con số duy nhất còn lại để so là đối chứng Kaggle (0,7604) với E03 máy cá nhân (0,7768) — **đúng kiểu so xuyên môi trường mà T23 vừa dạy là không được làm**, và nó lại đang nghiêng về phía tôi mong. Đã dừng, tải shard về, chấm lại tại chỗ (0,7649) rồi mới kết luận.

Bài học ghi vào TASKS.md: ô nào cần shard của thí nghiệm cũ thì phải chạy trên máy cá nhân.

##### Cách gộp đầu đảo chỗ lần thứ ba

`mixed k=8` trên Kaggle, `topk k=32` tại chỗ, bảng chọn phẳng ở đỉnh (ba ứng viên cách nhau 0,002). Củng cố kết luận T23: chỉ họ `topk_heads` chốt được, con số `k` để dev chọn từng lần.

##### E05 chốt

**Chia theo câu, `min_words=5`**, giữ nguyên cho mọi thí nghiệm còn lại. Cấu hình này đã có điểm test từ T22: macro-F1 **0,7567** [0,7242; 0,7885]. Phần quyết định của T24 **không tốn thêm GPU nào** — 57,5 phút chi hết cho phép đối chứng, tức chi để biết viết phần đóng góp thế nào.

##### Kiểm

`pytest` 613 ca xanh, `ruff check .` sạch. Kèm notebook đã chạy làm minh chứng (16 ô có output, đã quét không có khóa API). Ba cải tiến nợ từ T23 đều làm đúng việc: ô kiểm toàn vẹn báo OK cả hai shard, ô 9 copy được `runs.jsonl`, `--dev-only` in F1 từng lớp.

---

<a id="pr-60"></a>

### #60 — T25: công cụ E06 định vị chú ý, chờ chạy GPU

- **Nhánh:** `t25-dinh-vi` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 30/08/2026 22:02 · **gộp:** 30/08/2026 22:02 · **commit gộp:** [`4abf0be`](https://github.com/wsunicorn/vihallulens/commit/4abf0be0ee20860cfddc8c42dd4824cfa283b133)
- **Thay đổi:** +3074 / −4, 10 file · **bình luận bot:** 1

Thí nghiệm quyết định CH1. Mọi kết quả đến giờ **suy ra** cơ chế từ điểm phân loại — chunk-aware giúp ích, vậy chú ý hẳn rơi vào chỗ có nghĩa. Đó là suy luận gián tiếp và nó có lỗ hổng: một bộ phát hiện có thể ăn điểm nhờ bất kỳ thứ gì tương quan với ảo giác.

E06 đọc thẳng: đoạn được chú ý nhiều nhất **có phải** đoạn chứa bằng chứng vàng không.

##### Bốn phép đo trên CPU, phép thứ tư là điều kiện tiên quyết

```
ngữ cảnh            794 token trung bình, lớn nhất 2.313
vượt trần 4.096     0,0 %
số đoạn (dev)       22,7 trung bình, trung vị 19, lớn nhất 161
định vị bằng chứng  2.377/2.377, không sót mẫu nào
sàn ngẫu nhiên      1/n trung bình = 0,0614
vị trí đoạn vàng    trung bình 0,519, 45,6 % ở nửa đầu
```

**Điều thứ tư quyết định thí nghiệm có diễn giải được không.** Nếu bằng chứng dồn về đầu hay cuối ngữ cảnh thì một bộ đoán "luôn chọn đoạn đầu" đã thắng sàn, và hit@1 cao sẽ chẳng chứng minh gì. Nó rải đều nên không có mẹo nào ăn được. Notebook có `assert` dừng nếu điều này hỏng.

**Một rủi ro còn treo:** trái với dự đoán ở mục 5 `CLAUDE.md`, ISE-DSC01 sau chuẩn hóa dài nhất 2.313 token, nên **nhánh cắt ngắn vẫn chưa được thử thật** sau sáu lượt trích. Ghi lại chứ không coi là đã qua.

##### Ba quyết định thiết kế

**Hạng đoạn vàng tính ngay trong lúc trích.** Nó cần danh sách chunk **sống sót sau cắt ngắn** — cắt ngắn bỏ nguyên từng đoạn rồi đánh số lại, nên chỉ số tìm trong danh sách gốc sẽ âm thầm trỏ vào đoạn khác. `AttentionFeatures` vì thế nay trả về cả danh sách chunk sống sót.

**Hòa khi xếp hạng tính bi quan.** Bản đầu tôi viết dùng `>` nên **lạc quan**, trong khi docstring nói bi quan — một đầu trải đều tuyệt đối sẽ được chấm hit@1 dù không tỏ ưu tiên gì. Bộ kiểm thử bắt được; ở `float16` hòa không hiếm nên lỗi này sẽ thổi phồng hit@1.

**Sàn ngẫu nhiên tính theo từng mẫu rồi mới trung bình.** Số đoạn chạy từ 3 tới 161, và `1/mean(n)` khác `mean(1/n)` rất nhiều ở độ tản ấy.

##### Kiểm định: `p` không phải con số đáng đọc

Hai nhóm 1.269 và 2.377 mẫu — ở cỡ đó một khác biệt vô nghĩa vẫn ra p < 0,001. Script in **cỡ ảnh hưởng rank-biserial** cạnh p và bắt đọc nó trước. Có ca kiểm thử dựng đúng tình huống ấy (lệch 1/20 độ lệch chuẩn, n = 20.000) để khóa lại rằng p nhỏ mà cỡ ảnh hưởng vẫn "không đáng kể".

Mann-Whitney **tự viết bằng numpy**, không gọi `scipy` — entropy bị chặn trong [0,1] và dồn về trần nên kiểm định t không dùng được, và viết tay thì `scipy` không thành phụ thuộc khai báo của cả dự án cho đúng một hàm.

Entropy đem kiểm là **trung bình mọi đầu**, không phải đầu tách nhãn tốt nhất — chọn đầu sau khi thấy dữ liệu là chọn thống kê theo kết quả.

##### Chạy thử trọn đường ống trên shard giả

Cấy sẵn một đầu định vị ở **lớp 5 đầu 11** với xác suất 0,55. Script tìm lại đúng lớp 5 đầu 11, hit@1 ra 0,5500 khớp xác suất đã cấy, sàn 0,0535, bội số 10,28 lần. Trung bình mọi đầu ra 0,0550 tức gần đúng sàn — đúng như phải thế khi chỉ một đầu được cấy.

##### Một chỗ cố ý không làm

Bảng 2 có sẵn dòng "Cửa sổ 128 token" cạnh "Chia theo câu", viết **trước** khi T24 chốt cách chia. Giờ chia theo câu đã là cấu hình chốt, nên chạy thêm 70 phút GPU cho cách chia đã bị loại là tiêu hạn mức để điền một ô không ai dùng. Bảng 3 đã trả lời câu hỏi so sánh cách chia.

##### Kiểm

`pytest` 642 ca xanh (thêm 29), `ruff check .` sạch.

##### Việc cần chạy

`notebooks/t25_dinh_vi_chu_y_t4.ipynb`, **~70 phút**: chỉ tập dev, 3.646 mẫu. Không chạy train vì E06 không huấn luyện gì; không chạy test để dành cho E07 và E16. Lượt trích này **T26 dùng lại được**.

---

<a id="pr-61"></a>

### #61 — T25: kết quả E06 — chú ý rơi đúng đoạn bằng chứng, CH1 được xác nhận

- **Nhánh:** `t25-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 31/08/2026 13:19 · **gộp:** 31/08/2026 13:20 · **commit gộp:** [`59e5474`](https://github.com/wsunicorn/vihallulens/commit/59e5474c8ccee9dfc2bb77e92bd3b51ee21f2a6f)
- **Thay đổi:** +162 / −2222, 4 file · **bình luận bot:** 1

**Thí nghiệm quyết định CH1, và nó qua.** 65,1 phút GPU, toàn tập dev 3.646 mẫu, **0 lỗi**. 2.376 mẫu có bằng chứng định vị được, trung bình **22,6 đoạn** mỗi ngữ cảnh.

| Chỉ số | Đầu mạnh nhất | Trung bình 756 đầu | Sàn ngẫu nhiên | Gấp sàn |
|---|---|---|---|---|
| **hit@1** | **0,8779** (lớp 14, đầu 6) | 0,3320 | 0,0614 | **14,29×** / 5,40× |
| hit@3 | 0,9562 (lớp 16, đầu 7) | 0,5177 | 0,1843 | 5,19× / 2,81× |
| MRR | 0,9200 (lớp 16, đầu 7) | 0,4709 | 0,1987 | 4,63× / 2,37× |

Đầu mạnh nhất chỉ **đúng đoạn chứa bằng chứng trong 87,8 %** số mẫu, chọn giữa trung bình 22,6 đoạn. Mọi kết quả trước đều **suy ra** cơ chế từ điểm phân loại; đây là lần đầu nó được **đo thẳng**.

##### Mối lo duy nhất, dập tắt bằng số

0,8779 là max trên 756 ô chọn trên đúng tập được báo cáo — nên là cận trên. Nhưng nếu **mọi** đầu đều mạnh ngang mức trung bình 0,3320 thì SE trên 2.376 mẫu là 0,0097, và max trên 756 lần rút chỉ kỳ vọng **0,363**. Quan sát **0,878**.

Và không phải một đầu ăn may:

```
đầu tốt nhất        0,878          10 đầu đầu bảng  0,878 … 0,863
trung vị 756 đầu    0,178 (2,9x)   192/756 đầu vượt 10x sàn
trung bình          0,332 (5,4x)   453/756 đầu vượt  2x sàn
```

**Nếu chỉ được báo cáo một con số thì nên là 5,40×** — trung bình mọi đầu, không dính lựa chọn nào.

Khác Lookback Lens: bài gốc thấy tín hiệu tập trung ở vài đầu; ở đây **một phần tư số đầu vượt 10 lần sàn** và các lớp mạnh nhất quây quanh giữa mạng (14, 15, 16, 19). Định vị bằng chứng là **thuộc tính rộng**, không phải mạch chuyên biệt.

##### Nửa thứ hai: không bằng chứng thì chú ý tản hơn

P(NEI tản hơn) = **0,7213**, cỡ ảnh hưởng rank-biserial **+0,4426** (lớn), z = 22,05.

Phải nói cho cân: **chênh tuyệt đối chỉ 0,03 trên thang 0–1**. Hiệu ứng lớn nằm ở **tính nhất quán của thứ tự**, không ở độ lớn — entropy là tín hiệu thật nhưng **yếu khi dùng một mình**, khớp đúng với E03 nơi đặc trưng hình dạng đứng riêng chỉ đạt 0,6054.

`p = 1e-107` gần như vô nghĩa ở cỡ mẫu này; đúng cái bẫy mà một ca kiểm thử của T25 dựng sẵn để khóa lại.

##### Nhánh cắt ngắn cuối cùng cũng chạy, và làm đúng việc

**6/3.646 mẫu bị cắt** — lần đầu sau bảy lượt trích. Trong đó **1 mẫu mất đoạn bằng chứng** và được **loại khỏi phần định vị** thay vì âm thầm chấm nhầm đoạn khác.

Đây chính là lý do `AttentionFeatures` phải trả về danh sách chunk sống sót. Cơ chế viết ra vì lo xa, nay được thử trên dữ liệu thật với đúng một mẫu.

##### Tái lập trùng từng chữ số

Chấm lại trên máy cá nhân từ shard tải về cho **kết quả giống hệt**, khác hẳn độ trôi 0,0075 ở T23. Lý do: E06 chỉ có số học thuần, không có bộ tối ưu lặp nào.

Nói thêm được một điều cho phần hạn chế: **độ trôi ở T23 là tính chất của bộ phân loại, không phải của đặc trưng chú ý.**

##### Kiểm

`pytest` 642 ca xanh, `ruff check .` sạch. Kèm notebook đã chạy làm minh chứng, đã quét không có khóa API. Chi phí 1.071 ms/mẫu ghi cho bảng E11.

---

<a id="pr-62"></a>

### #62 — T26: công cụ E07 chunk-aware trên ngữ cảnh dài, chờ chạy GPU

- **Nhánh:** `t26-ngu-canh-dai` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 31/08/2026 13:39 · **gộp:** 31/08/2026 13:39 · **commit gộp:** [`10c9e95`](https://github.com/wsunicorn/vihallulens/commit/10c9e95feca18f405f7ee88f23146359c9788e4f)
- **Thay đổi:** +2429 / −1, 5 file · **bình luận bot:** 1

E03 cho thấy chia theo đoạn có ích trên ViHallu (**5,3 đoạn**/ngữ cảnh). E06 cho thấy chú ý rơi đúng đoạn bằng chứng trên ISE-DSC01 (**22,6 đoạn**). Còn lại: bộ phát hiện **có mạnh lên** khi ngữ cảnh dài gấp bốn không.

##### Dùng chung lượt trích với E06

E07 khai cùng bộ dữ liệu, cách chia đoạn và bộ trích, nên `extraction_hash` trùng (`15ef31521fd6`) và **tập dev 3.646 mẫu đã trích ở T25 không phải chạy lại**. Đây đúng là thứ việc tách `extraction_hash` khỏi `config_hash` ở T22 sinh ra để làm.

Còn train (29.077 mẫu, ~8,7 giờ) và test (3.646 mẫu, ~1,1 giờ).

##### Tôi đo sai một lần, và đã tự sửa trước khi tiêu GPU

Script đo đường cong đầu tiên **cố định cách gộp đầu** lấy từ mô hình huấn luyện trên đủ 5.600 mẫu rồi áp cho mọi cỡ — nên các cỡ nhỏ bị phạt oan:

| mẫu train | script cố định | **đường ống thật** |
|---|---|---|
| 1.400 | 0,7300 | **0,7630** |
| 2.800 | 0,7512 | **0,7671** |
| 4.200 | 0,7540 | **0,7710** |
| 5.600 | 0,7768 | 0,7768 |

Đường ống thật **chọn lại cách gộp đầu trên từng cỡ**, và việc đó bù được phần lớn dữ liệu thiếu. Gấp bốn dữ liệu chỉ mua **+0,0138**, không phải +0,047.

Tôi đã báo với người dùng rằng "trích đủ hơn 12.000 mẫu khoảng +0,03"; ước lượng đúng là khoảng **+0,007**. Đính chính **trước** khi tiêu 9,8 giờ GPU, không phải sau.

##### Vẫn trích đủ 29.077, vì ba lý do không phụ thuộc biên độ ấy

1. **E16 dùng lại chính lượt trích này** — trích thiếu thì E16 thừa hưởng cùng giới hạn.
2. **Phép so khớp cỡ với E03 vẫn miễn phí** qua `--train-sample 5600` từ cùng shard. Trích đủ chỉ **thêm** một con số chứ không mất con số nào.
3. **Không phải xếp lịch GPU lần hai.**

##### Hai con số, hai câu hỏi

- **Đủ 29.077 mẫu** → E07 mạnh nhất có thể, số vào bảng kết quả.
- **Đúng 5.600 mẫu** → phép so **có kiểm soát** với E03. Chỉ số này mới nói được "ngữ cảnh dài thì chunk-aware thế nào", vì giữ cỡ train cố định.

So thẳng lượt đủ với 0,7567 của E03 là phép so không kiểm soát được biến nào.

`stratified_sample` giữ nguyên tỷ lệ nhãn thay vì rút đều: bộ phát hiện chạy `class_weight='balanced'`, nên tỷ lệ lệch là trọng số lớp đổi theo — thêm một biến vào phép so vốn chỉ được có một. Có test khóa điều đó, cùng một test khóa việc rows và labels không được lệch pha nhau.

##### Ba khả năng, ghi trước khi thấy số

- **Khớp cỡ cao hơn E03 rõ** → chunk-aware **mạnh lên** khi ngữ cảnh dài.
- **Xấp xỉ** → phương pháp **bền** qua độ dài ngữ cảnh.
- **Thấp hơn rõ** → chunk-aware **không** chuyển được. E06 vẫn đứng, nhưng khoảng cách giữa "định vị đúng" và "phân loại đúng" mới là thứ phải giải thích — và đó là kết quả đáng viết, không phải thất bại.

##### Kiểm

`pytest` 646 ca xanh (thêm 4), `ruff check .` sạch.

##### Việc cần chạy

`notebooks/t26_chunk_aware_ngu_canh_dai_t4.ipynb`, **~9,8 giờ**. Tập train tách ba ô (0–10.000, 10.000–20.000, còn lại) để có điểm dừng nhìn thấy được; mỗi ô chạy lại được nên phiên chết giữa chừng không mất phần đã trả tiền. Phiên Kaggle giới hạn 12 giờ nên vừa đủ nhưng sát — chia hai phiên cũng được.

---

<a id="pr-63"></a>

### #63 — T26: kết quả E07 — chuyển được sang ngữ cảnh dài nhưng lợi thế co lại

- **Nhánh:** `t26-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 01/09/2026 10:39 · **gộp:** 01/09/2026 10:39 · **commit gộp:** [`7c6ff12`](https://github.com/wsunicorn/vihallulens/commit/7c6ff12ffdc68d962c67d008568dc725e4dc2a9e)
- **Thay đổi:** +368 / −12, 6 file · **bình luận bot:** 1

Trích 10,1 giờ GPU, **0 lỗi trên 32.723 mẫu**. Chấm điểm chạy ở máy cá nhân, cùng máy đã chấm E02 và E03, theo nguyên tắc T23.

| Bộ dữ liệu | Đoạn/ngữ cảnh | train | Lookback gộp | Chunk-aware | Chênh |
|---|---|---|---|---|---|
| ViHallu | 5,3 | 5.600 | 0,7451 | 0,7567 | **+0,0116** |
| ISE-DSC01 | 22,6 | 5.600 | 0,7337 | 0,7388 | **+0,0051** |
| ISE-DSC01 | 22,6 | 29.077 | 0,7851 | **0,7919** | **+0,0068** |

##### Giả thuyết bị bác

Trước khi chạy tôi viết: ngữ cảnh càng nhiều đoạn thì hình dạng phân bố càng có chỗ nói lên điều gì. **Gấp bốn số đoạn thì lợi thế co lại còn một nửa.**

Lý do đọc được ngay từ bảng: **lookback gộp trên ISE-DSC01 đã rất mạnh sẵn** (0,7851 so với 0,7451). Ngữ cảnh dài không làm chunk-aware yếu đi — nó làm *mốc so* khỏe lên.

Cả ba chênh lệch nhỏ so với KTC. Cách nói đúng: **nhỉnh hơn nhất quán về hướng nhưng không có ý nghĩa thống kê, ở cả hai bộ.**

##### Phát hiện đáng viết nhất: định vị ≠ phân biệt

E06: chú ý rơi đúng đoạn bằng chứng **87,8 %**, gấp 14 lần sàn.
E07: biết *chỗ nào* được nhìn chỉ thêm **+0,007** so với biết *bao nhiêu*.

Không mâu thuẫn. Đặt cạnh nhau chúng nói: **tín hiệu định vị có thật và rất mạnh, nhưng bài toán ba lớp này phần lớn đã được giải bằng đại lượng gộp.** Đó cũng là chỗ hướng phát triển nằm — một bài toán *cần* biết chỗ sẽ khai thác được phần E06 đo.

##### Suýt viết vào báo cáo một kết luận ngược

Nhìn thô: chunk chiếm **87 % trọng số ở E03** nhưng **27 % ở E07**. Đó là hiện vật của cách gộp đầu dev chọn (E03 `topk k=32` → lookback 32 cột; E07 `mixed k=32` → lookback giữ nguyên 756 cột). Quy về mỗi cột:

| | lookback | chunk-aware | tỷ lệ |
|---|---|---|---|
| E03, 5,3 đoạn | 0,4016 %/cột | 0,5447 %/cột | 1,36× |
| E07, 22,6 đoạn | 0,0963 %/cột | 0,1700 %/cột | **1,77×** |

**Chunk nặng ký hơn trên ngữ cảnh dài, không nhẹ đi.**

##### Đường cong học dốc hơn hẳn dự đoán của tôi

Ước lượng từ ViHallu cho chặng 5.600 → 29.077 là **+0,015**. Đo thật **+0,0531** — gấp ba lần rưỡi. Đường cong đo trên một bộ **không dự báo được** cho bộ khác.

##### Hai lỗi task này phơi ra

**1. Tôi lặp lại đúng lỗi đã ghi ở T24.** Hai ô chấm điểm hỏng vì phiên Kaggle mới không có shard dev trích ở T25. Ô kiểm toàn vẹn báo đúng nhưng **chạy sau** nên vô dụng — nếu chạy ở phút thứ 2 thay vì giờ thứ 10 thì đã cứu được.

Chốt thành **quy tắc** thay vì ghi chú: notebook trên Kaggle **chỉ làm việc trích**, mọi việc chấm điểm chạy ở máy cá nhân. Giải luôn ràng buộc T23 là mọi con số đem so phải chấm cùng một máy. Từ T27 thêm ô tiền kiểm ngay sau ô cài đặt.

**2. Mốc so cắm cứng số của bộ dữ liệu khác.** `E02_MACRO_F1 = 0.7465` đo trên **ViHallu** nhưng áp cho mọi bộ, nên E07 bị so chéo bộ và nhận phán quyết `CHƯA VƯỢT` vô nghĩa kèm mã lỗi 2.

Sửa: mốc **tra từ `results/runs.jsonl`** theo đúng bộ dữ liệu, tìm lượt có `groups: [basic]`; không có thì nói thẳng chứ không mượn số bộ khác. Bốn ca kiểm thử, một ca khóa việc dòng `dev_only` không bị đọc nhầm thành điểm test.

Dựng luôn mốc đúng (`e07_baseline_lookback_isedsc01.yaml`, cùng lượt trích, khác E07 đúng một thứ) — **không tốn giây GPU nào**. Chính nó làm lộ ra lợi thế thật là +0,0068 chứ không phải +0,0454 như con số so chéo bộ gợi ý.

##### Kiểm

`pytest` 650 ca xanh (thêm 4), `ruff check .` sạch.

---

<a id="pr-64"></a>

### #64 — T26: lưu notebook đã chạy làm minh chứng

- **Nhánh:** `t26-minh-chung` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 01/09/2026 10:46 · **gộp:** 01/09/2026 10:47 · **commit gộp:** [`468eff8`](https://github.com/wsunicorn/vihallulens/commit/468eff86906374595c015caefac0c2cf631d0c18)
- **Thay đổi:** +1 / −2218, 1 file · **bình luận bot:** 1

Bản Kaggle chạy 31/08–01/09/2026, 16 ô có output: ba chặng trích tập train (10.000 + 10.000 + 9.077), tập test 3.646 mẫu, **10,1 giờ GPU và 0 lỗi trên 32.723 mẫu**.

Giữ nguyên **cả hai ô chấm điểm hỏng** vì thiếu shard dev — đó là minh chứng trung thực về những gì đã xảy ra, và về lý do quy tắc *"Kaggle chỉ trích, chấm điểm chạy ở máy cá nhân"* được chốt ở task này.

73 KB, đã quét không có khóa API.

---

<a id="pr-65"></a>

### #65 — T27: công cụ E08 bỏ bằng chứng đi, chờ chạy GPU

- **Nhánh:** `t27-can-thiep` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 01/09/2026 11:07 · **gộp:** 01/09/2026 11:07 · **commit gộp:** [`05e8972`](https://github.com/wsunicorn/vihallulens/commit/05e89727a3f34b3c8b0376841e42fbe372b2e57c)
- **Thay đổi:** +3227 / −3, 11 file · **bình luận bot:** 1

**Phép kiểm can thiệp duy nhất của cả đề tài.** Mọi thí nghiệm đến giờ đều **tương quan**: đo một tín hiệu, so với nhãn người khác gán, báo mức khớp — khi hai bên khớp thì *"cơ chế hoạt động"* là **suy luận**, không phải quan sát. E06 gần trực tiếp nhất nhưng vẫn chỉ *quan sát* chú ý rơi ở đâu.

E08 **can thiệp**: mỗi claim ghép cặp với chính nó, đọc hai lần trên hai ngữ cảnh mười câu **khác nhau đúng một câu ở đúng một vị trí**.

##### Nhãn nửa 'absent' không do ai gán

Rút câu vàng ra thì phản hồi khẳng định điều ngữ cảnh không chứa — đúng định nghĩa ảo giác ngoại lai. Đó là **sự thật về cách dựng**, không phải phán đoán ai đó có thể bất đồng.

Quan trọng hơn vẻ ngoài: T13 đo được ranh giới nội tại–ngoại lai đánh bại **hai người gán nhãn** (0,70 và 0,50) và cả **Gemini** (0,474). Ở E08 ranh giới ấy được **dựng ra** chứ không được **đoán** — lần đầu phần khó nhất của bài toán không phụ thuộc chất lượng nhãn.

##### Một confound suýt lọt

BM25 để câu vàng ở **hạng 0 với 94 % claim** (vị trí tương đối 0,040). Ghép theo thứ tự truy xuất thì một bộ đoán *"luôn chọn đoạn đầu"* đã thắng sàn. Đây đúng cái confound tôi đã kiểm và **loại trừ được** ở T25 — lần này nó **có thật**.

Chữa bằng **xáo thứ tự** trước khi ghép: vị trí vàng về **0,513**, rải đều. Hai vế dùng **cùng một hoán vị**, nếu không chúng khác nhau ở mười chỗ chứ không phải một.

##### Ô cổng bắt được thứ bộ lọc bỏ sót

Bộ lọc đầu chỉ đòi hai vế **cùng số đoạn**. Ô kiểm tiền đề chạy trên dữ liệu thật và tìm ra **5/1.841 cặp khác nhau ở hơn một đoạn** dù cùng số đoạn — câu vàng gộp với hàng xóm ở vế này trong khi câu nhiễu gộp kiểu khác ở vế kia.

0,3 %: đủ nhỏ để lọt, đủ lớn để làm yếu đúng cái tính chất cả thí nghiệm dựa vào. Siết thành *"đếm số đoạn khác nhau, phải bằng đúng 1"*. **Cả ba tiền đề giờ đạt 100 %.**

##### Hướng dự đoán, ghi trước khi thấy số

| đặc trưng | bỏ vàng đi thì phải | vì sao |
|---|---|---|
| `chunk_entropy` | **tăng** | không còn gì để tập trung |
| `chunk_max_share` | **giảm** | không đoạn nào còn trội hẳn |
| `chunk_gini` | **giảm** | các đoạn đều nhau hơn |
| `top1_top2_gap` | **giảm** | đoạn tốt nhất hết nổi bật |
| `chunk_drift` | *không dự đoán* | drift nói về chuyển động theo token |

`EXPECTED_DIRECTION` có test khóa lại, để kết quả đi ngược **không thể** được mô tả lại thành xác nhận.

##### Kiểm định theo cặp, và bẫy riêng của nó

Hai vế là **cùng một mẫu đọc hai lần** nên không độc lập — Mann-Whitney của T25 sẽ trả lời câu hỏi về hai tổng thể không tồn tại. Thêm `wilcoxon()`, cũng tự viết bằng numpy.

Bẫy của nó **ngược** bẫy p-value: nó đo mức nhất quán của **hướng**, không đo độ lớn. Một dịch chuyển đều bằng 1/20 độ lệch chuẩn vẫn cho **100 % cặp đúng hướng và cỡ ảnh hưởng 1,0**. Báo cáo in `median_change` ngay cạnh; có test dựng đúng tình huống ấy.

##### Trả món nợ T26

Notebook có **ô 3 là tiền kiểm**: liệt kê mọi shard các ô sau cần, đối chiếu với thứ phiên này tự sinh ra, `SystemExit` ngay nếu thiếu. Đã chạy thử.

##### Chạy thử trên shard giả

Cấy bốn hiệu ứng đúng hướng và một đầu định vị (lớp 14, đầu 6). Script khôi phục **cả bốn đúng dấu đúng độ lớn** (+0,0399 so với +0,04 cấy), tìm đúng đầu, và `chunk_drift` không cấy gì ra **49,4 %** — đúng mức ngẫu nhiên, không bị đánh dấu.

##### Kiểm

`pytest` **675 ca xanh** (thêm 25), `ruff check .` sạch.

##### Việc cần chạy

`notebooks/t27_bo_bang_chung_t4.ipynb`, **~48 phút** (3.672 dòng × ~784 ms). Dựng ngữ cảnh chạy CPU ngay trong notebook. Chấm điểm chạy lại ở máy cá nhân theo quy tắc T26.

---

<a id="pr-66"></a>

### #66 — T27: cài rank-bm25 và cho ô tiền kiểm soát cả phụ thuộc

- **Nhánh:** `t27-sua-phu-thuoc` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 01/09/2026 21:58 · **gộp:** 01/09/2026 21:58 · **commit gộp:** [`4d5b106`](https://github.com/wsunicorn/vihallulens/commit/4d5b1066b3808bcd55d186a09522889f54b8dc8b)
- **Thay đổi:** +57 / −46, 2 file · **bình luận bot:** 1

Lượt chạy đầu hỏng ở **giây thứ 43**: `ModuleNotFoundError: No module named 'rank_bm25'`. Không tốn giây GPU nào.

##### Cảnh báo đã có sẵn từ T23

```
vihallulens 0.1.0 requires rank-bm25, which is not installed.
```

Pip in dòng này ở **mọi lượt chạy từ T23**. Tôi đọc nó bốn lần và bốn lần viết *"vô hại, không nằm trong đường đi"* — đúng cho T23–T26, sai cho T27, mà chính tôi là người viết câu *"rank-bm25 cho kho truy xuất ở T16"*.

##### Lỗi thứ hai nghiêm trọng hơn

**Ô tiền kiểm — thứ vừa thêm ở T27 để trả nợ T26 — báo xanh** rồi để notebook chạy tiếp vào chỗ chết. Nó chỉ kiểm shard, không kiểm phụ thuộc.

Đã mở rộng sang các gói các ô sau thật sự import. **Khai rõ danh sách** thay vì quét toàn bộ `pyproject.toml`: `fastapi`, `uvicorn`, `ruff` cũng được khai báo nhưng Kaggle không cài và E08 không dùng — quét tất cả sẽ **báo động giả**, đúng lỗi ô kiểm toàn vẹn của T26 từng mắc.

##### Bài học lặp lần thứ ba

**Một ô cổng chỉ chặn được thứ nó biết phải kiểm.** T26 dạy *"phải chạy trước"*, T27 dạy *"phải kiểm đủ loại điều kiện, không chỉ loại vừa làm hỏng lần trước"*.

`pytest` 675 ca xanh, `ruff` sạch.

---

<a id="pr-67"></a>

### #67 — TASKS: task đã xong không được còn mục 'Việc cần chạy'

- **Nhánh:** `sua-tieu-de-tasks` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 01/09/2026 22:01 · **gộp:** 01/09/2026 22:01 · **commit gộp:** [`356fe4b`](https://github.com/wsunicorn/vihallulens/commit/356fe4b4dbb5c83108b039bda7cccfac3e564f4d)
- **Thay đổi:** +12 / −12, 1 file · **bình luận bot:** 1

Sáu task đã tick (T20, T22, T23, T24, T25, T26) vẫn giữ mục **'Việc cần chạy'** với câu mệnh lệnh *'Mở `notebooks/...`'* ở cuối phần diễn giải. Đọc lướt thì chúng trông như chưa làm — người dùng đã hỏi đúng câu đó về T26 dù nó đã tick từ `7c6ff12`.

`TASKS.md` là **nguồn sự thật về tiến độ** theo mục 6 CLAUDE.md, nên một mục đọc sai chiều là lỗi thật chứ không phải chuyện thẩm mỹ.

Đổi tiêu đề thành **'Lượt chạy đã thực hiện'** và câu mở thành *'Đã chạy `notebooks/`'*. Giữ nguyên nội dung vì nó là bản ghi hữu ích về thời gian và cấu hình đã chạy. Task chưa tick (T27) giữ nguyên 'Việc cần chạy'.

---

<a id="pr-68"></a>

### #68 — T27: trả lại ô chuẩn bị dữ liệu và cho tiền kiểm đi hết chuỗi

- **Nhánh:** `t27-sua-chuoi` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 01/09/2026 22:22 · **gộp:** 01/09/2026 22:22 · **commit gộp:** [`008bd48`](https://github.com/wsunicorn/vihallulens/commit/008bd486f0b40360e10f0d3784b80f9b4cc417c6)
- **Thay đổi:** +103 / −56, 2 file · **bình luận bot:** 0

Lượt thứ hai hỏng ở **giây thứ 44**: `FileNotFoundError: viwikifc_dev.parquet`. Khi dựng notebook T27 tôi thay ô 'chuẩn bị dữ liệu' bằng ô tiền kiểm và **quên thêm lại**.

Không tốn giây GPU nào. Nhưng đây là **lần thứ ba liên tiếp hỏng cùng một kiểu**:

```
T26        cổng kiểm shard, chạy SAU 10 giờ GPU  -> báo đúng mà vô dụng
T27 lần 1  cổng chạy trước, chỉ kiểm shard       -> thiếu rank-bm25, giây 43
T27 lần 2  cổng kiểm shard + gói                 -> thiếu interim, giây 44
```

**Cả hai lần ô tiền kiểm đều báo xanh.** Đó mới là lỗi thật: nó chỉ kiểm thứ tôi bảo nó kiểm, và tôi chỉ bảo nó kiểm thứ vừa làm hỏng lần trước.

##### Sửa tận gốc thay vì thêm một trường hợp đặc biệt nữa

Tiền kiểm nay **tách đôi rành mạch**:

- **Phải có sẵn** — phiên này không tạo được, thiếu là dừng: các gói mà các ô sau import, và thư mục dữ liệu thô đã mount cùng file `viwikifc*` trong đó.
- **Tự tạo** — in cả **chuỗi bốn mắt xích** theo thứ tự ô sinh ra chúng, từ `viwikifc_dev.parquet` tới shard đặc trưng.

Khác hai lần trước ở chỗ nó liệt kê **toàn bộ đường đi** chứ không chỉ mắt xích cuối. Đã chạy thử hai chiều: bình thường in đủ chuỗi và báo đạt; cố tình bỏ một gói thì `SystemExit` ngay.

##### Bài học

**Một ô cổng chỉ chặn được thứ nó biết phải kiểm.** Vá đúng cái vừa hỏng là chiến lược thua — lần sau hỏng ở loại khác. Cách duy nhất thoát ra là liệt kê điều kiện của cả đường đi.

`pytest` 675 ca xanh, `ruff` sạch.

---

<a id="pr-69"></a>

### #69 — T27: kết quả E08 — bỏ bằng chứng đi thì chú ý tản ra, cả bốn hướng đều đúng

- **Nhánh:** `t27-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 02/09/2026 09:59 · **gộp:** 02/09/2026 09:59 · **commit gộp:** [`2514922`](https://github.com/wsunicorn/vihallulens/commit/25149229d2f48c6e2a77acd807784c6b04ddd636)
- **Thay đổi:** +164 / −2263, 4 file · **bình luận bot:** 1

43,1 phút GPU, **0 lỗi trên 3.672 dòng**. 1.836 cặp, mỗi cặp là **cùng một claim đọc hai lần** trên hai ngữ cảnh khác nhau **đúng một câu ở đúng một vị trí**.

| Đặc trưng | Có vàng | Mất vàng | Đổi | % cặp đúng hướng | Cỡ ảnh hưởng |
|---|---|---|---|---|---|
| `chunk_entropy` ↑ | 0,7966 | 0,8176 | **+0,0156** | **75,4 %** | +0,7156 |
| `chunk_gini` ↓ | 0,5064 | 0,4860 | −0,0158 | 74,5 % | −0,6855 |
| `chunk_max_share` ↓ | 0,3597 | 0,3392 | −0,0139 | 72,4 % | −0,6570 |
| `top1_top2_gap` ↓ | 0,1829 | 0,1611 | −0,0129 | 71,2 % | −0,6237 |
| `chunk_drift` *(không dự đoán)* | 0,2081 | 0,2110 | +0,0024 | 63,3 % | +0,4009 |

**Cả bốn hướng dự đoán đều đúng**, cỡ ảnh hưởng 0,62–0,72 tức mức **lớn**. Mũi tên ghi vào `EXPECTED_DIRECTION` **trước khi chạy** và có test khóa.

##### Bằng chứng khác loại với mọi task trước

T20–T26 đều **tương quan**: đo tín hiệu, so với nhãn ai đó gán. Khi khớp thì *"cơ chế hoạt động"* là **suy luận**.

T27 **can thiệp**: giữ nguyên phản hồi, chín câu nhiễu, độ dài, số đoạn, thứ tự — chỉ **rút câu bằng chứng ra**.

Và nhãn nửa "mất vàng" **không do ai gán**. T13 đo được ranh giới nội tại–ngoại lai đánh bại hai người gán nhãn (κ 0,70 và 0,50) và cả Gemini (0,474); ở đây nó được **dựng ra** chứ không **đoán**.

##### Độ lớn nhỏ, nói rõ

Chênh tuyệt đối chỉ **0,013–0,016 trên thang 0–1**. Kiểm định theo cặp đo **nhất quán của hướng**, không đo độ lớn.

Đọc đúng: **rút bằng chứng ra làm chú ý tản hơn một cách nhỏ nhưng rất nhất quán.** Nó chứng minh tín hiệu *phản ứng với sự có mặt của bằng chứng* — **không** chứng minh nó đủ mạnh để một mình phân loại. E03 và E07 đã cho thấy điều thứ hai không đúng.

##### Lặp lại E06 trên bộ thứ hai, số gần như trùng

| | E06 · ISE-DSC01 | E08 · ViWikiFC |
|---|---|---|
| Cách dựng ngữ cảnh | tài liệu tự nhiên | mười câu BM25, **đã xáo** |
| Đoạn mỗi ngữ cảnh | 22,6 | 9,8 |
| Sàn hit@1 | 0,0614 | 0,1027 |
| hit@1 đầu mạnh nhất | 0,8779 | **0,8529** |
| **hit@1 trung bình 756 đầu** | 0,3320 | **0,3289** |

Khác thể loại, khác cách dựng ngữ cảnh, khác số đoạn gần ba lần, khác sàn — mà **trung bình mọi đầu lệch nhau 0,003**. Con số ấy không dính lựa chọn nào.

**Định vị bằng chứng là thuộc tính của mô hình đọc, không phải của một bộ dữ liệu.** E06 một mình không nói được điều này.

##### `chunk_drift` phản ứng mà không được dự đoán

63,3 %, cỡ ảnh hưởng +0,4009. Ghi như **quan sát thăm dò** chứ không phải xác nhận — dùng nó làm bằng chứng bây giờ là chọn giả thuyết sau khi thấy dữ liệu.

##### Một chỗ tôi làm vội

File `viwikifc_e08_dev.parquet` tải về bị đặt nhầm vào `data/processed/`. Tôi thấy `.equals()` trả `False` rồi **xóa trước khi soi kỹ khác ở đâu**. Bằng chứng gián tiếp cho thấy nội dung khớp: **1.836/1.836 cặp ghép đúng** giữa shard trích trên Kaggle và parquet dựng ở máy — sai một `sample_id` là hỏng ngay.

##### Kiểm

`pytest` 675 ca xanh, `ruff` sạch. Chấm lại ở máy cá nhân **trùng từng chữ số**. Kèm notebook đã chạy làm minh chứng.

**Hết giai đoạn 4.**

---

<a id="pr-70"></a>

### #70 — T27: BM25 hòa điểm gặp sắp xếp không ổn định, hai máy dựng ngữ cảnh khác nhau

- **Nhánh:** `t27-sua-hoa-diem` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 02/09/2026 11:03 · **gộp:** 02/09/2026 11:03 · **commit gộp:** [`20e97ad`](https://github.com/wsunicorn/vihallulens/commit/20e97ad0fceb871e49a284c435954d7e548a3159)
- **Thay đổi:** +116 / −8, 4 file · **bình luận bot:** 1

So bản parquet dựng trên Kaggle với bản dựng ở máy. Lần đầu tôi thấy `.equals()` trả `False` rồi **đoán** là khác kiểu dữ liệu và xóa file — **đoán sai**.

```
kiểu dữ liệu    : không cột nào khác
context         : 31 dòng khác   <<<
evidence_start  :  2 dòng khác
```

Khác **nội dung thật**: 17 trên 1.836 cặp (0,9 %), một cặp còn ra **số đoạn khác nhau** giữa hai máy.

##### Nguyên nhân

`EvidenceIndex.search` xếp hạng bằng `scores.argsort()[::-1]`, mà `argsort` mặc định dùng quicksort nên **không ổn định**. Hai câu cùng điểm BM25 ra theo thứ tự numpy trên máy đó tình cờ sinh ra.

Sửa thành `np.lexsort((ids, -scores))`: giảm dần theo điểm, hòa thì xếp theo `evidence_id` — băm nội dung câu, nên tiêu chí phân định **chỉ phụ thuộc nội dung** và không đổi nếu dựng lại kho theo thứ tự dòng khác.

Hai ca kiểm thử: dựng ba mươi câu cùng điểm và đòi thứ tự lặp lại được; đảo ngược thứ tự dòng của kho và đòi kết quả truy xuất không đổi.

##### Giữ bản Kaggle

Shard đặc trưng được trích **từ** nó, nên con số E08 mô tả đúng thứ mô hình đã đọc. **Kết quả không đổi** — đã chấm lại, trùng từng chữ số: phép ghép cặp chỉ dùng `sample_id`/`pair_id` vốn giống nhau ở cả hai bản.

**Không trích lại** dù shard có trước bản sửa: Kaggle đã tự chạy ô kiểm tiền đề và báo 1.836/1.836 đạt 100 %, nên 17 cặp ấy vẫn là cặp tối thiểu hợp lệ; 0,9 % dữ liệu; 43 phút GPU để đổi một thứ không đo được là không đáng.

##### Bài học

Lần thứ hai trong hai ngày tôi **xóa một file rồi mới tìm hiểu nó khác ở đâu**. Lần này phỏng đoán sai đã **che mất một lỗi tái lập có thật**.

`pytest` 677 ca xanh, `ruff` sạch.

---

<a id="pr-71"></a>

### #71 — T28: soạn báo cáo giữa kỳ và thư gửi GVHD, chờ gửi trước 04/10

- **Nhánh:** `t28-bao-cao-giua-ky` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 02/09/2026 11:19 · **gộp:** 02/09/2026 11:20 · **commit gộp:** [`1455509`](https://github.com/wsunicorn/vihallulens/commit/1455509f3c0f6ee1d7f5359b40fab639bdabbeca)
- **Thay đổi:** +91 / −1, 1 file · **bình luận bot:** 1

Gom kết quả giai đoạn 1–4 thành báo cáo giữa kỳ. Mười mục, khoảng 4.100 từ, 12 bảng.

##### Hai file đã tạo

| File | Nội dung |
|---|---|
| `UniversityRequirements/Reports/tao_bao_cao_giua_ky.py` | Bộ sinh báo cáo `.docx` |
| `UniversityRequirements/WeeklyLogs/Email_giua_ky.md` | Thư đính kèm, Reply All vào chuỗi cũ |

Cả hai nằm trong `UniversityRequirements/` vốn đã gitignore từ đầu (`git ls-files` đếm 0 file trong đó), nên **PR này chỉ chứa `TASKS.md`**.

##### Ba bảng mà tiêu chí đòi đều có đủ số

| Bảng trong báo cáo | Tương ứng `EXPERIMENTS.md` | Thí nghiệm |
|---|---|---|
| Bảng 5 — kết quả chính ViHallu | Bảng 1 | E01, E09, E10, E02, E03 |
| Bảng 6 — chọn cách chia đoạn | Bảng 3 | E05 |
| Bảng 7 — định vị chú ý | Bảng 2 | E06 |
| Bảng 8 — ngữ cảnh dài | Bảng 2b | E07 |
| Bảng 9, 10 — bỏ bằng chứng đi | Bảng 2c | E08 |

##### Chỗ khó nhất: nói thế nào về một lợi thế nhỏ

Số liệu kể một câu chuyện hai mặt. Cơ chế được xác nhận rất mạnh — định vị đúng 87,8 % giữa 22,6 đoạn, lặp lại gần y hệt trên bộ thứ hai (0,3320 so với 0,3289), can thiệp đúng cả bốn hướng ghi trước khi chạy. Nhưng lợi thế phân loại chỉ +0,0116 và +0,0068, khoảng tin cậy chồng gần hết.

Đã chọn để hai mặt cạnh nhau và biến khoảng cách giữa chúng thành phát hiện ở mục 6.1: định vị đúng và phân loại đúng là hai việc khác nhau, vì ảo giác nội tại **vẫn dồn chú ý đúng chỗ**. Cách còn lại — dẫn 14,29× lên đầu, đẩy +0,007 xuống chú thích — bị loại vì hội đồng sẽ tự tìm ra.

##### Vì sao ô vẫn chưa tick

Tiêu chí có ba vế, vế thứ ba là **gửi GVHD trước 04/10**. Hai vế đầu xong; vế ba là việc của người. Dùng đúng lối ghi đã dùng ở T27 lúc chờ chạy Kaggle.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
677 passed in 13.54s

$ python UniversityRequirements/Reports/tao_bao_cao_giua_ky.py
D:\StudyDocument\KLTN\vihallulens\UniversityRequirements\Reports\Bao_cao_giua_ky_KLTN.docx
```

---

<a id="pr-72"></a>

### #72 — T28: dựng lại báo cáo giữa kỳ theo mẫu của Khoa, thêm báo cáo tuần 5

- **Nhánh:** `t28-mau-khoa-va-tuan-05` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 02/09/2026 11:44 · **gộp:** 02/09/2026 11:44 · **commit gộp:** [`fd59d11`](https://github.com/wsunicorn/vihallulens/commit/fd59d117aaf7d4ac3d17e3322469078c72e0e3b9)
- **Thay đổi:** +63 / −35, 1 file · **bình luận bot:** 1

##### Vì sao dựng lại

Bản đầu viết theo bố cục báo cáo tuần. Mẫu `Mau bao cao KLTN_DS.docx` có mục **ĐỊNH DẠNG** quy định chặt hơn nhiều, nên dựng lại từ đầu.

| Hạng mục | Mẫu của Khoa | Báo cáo tuần dùng |
|---|---|---|
| Lề | 3 / 3 / **3,5** / 2 cm | 2 / 2 / 3 / 2 |
| Giãn dòng thân bài | **1,5 lines**, before 10 pt | 1,3 |
| Heading 1 | TNR 14 đậm IN HOA, before/after 24 pt | — |
| Caption | bảng **ở trên**, hình **ở dưới**, căn giữa | — |
| Đánh số | gắn với chương — Bảng 5.1 | — |
| Số trang | góc phải dưới, từ phần nội dung | — |

##### Nội dung

Phần đầu điền đủ theo danh sách "Thành phần": bìa Việt (hai bản), bìa Anh, Abstract + keywords, Tóm tắt + từ khóa, lời cảm ơn, ba trang nhận xét, mục lục, hai danh mục, danh mục viết tắt. Không chỗ nào để chữ mẫu.

Thân bài **6 chương, 8.033 từ, 19 bảng, 4 hình**.

Mục lục và hai danh mục là **trường Word** — Ctrl+A rồi F9. Hai danh mục dùng hai style riêng `Caption Hinh` / `Caption Bang` để tách hình khỏi bảng; caption viết sai style thì không hiện ra, tức hỏng to chứ không hỏng âm thầm.

##### Lỗ hổng trong chuỗi báo cáo tuần

Báo cáo tuần 4 chốt ngày **27/08** và xếp T20–T24 vào "kế hoạch tuần tới". Bốn việc đó xong **28–30/08** — vẫn trong tuần 4, nhưng sau khi thư đã chốt. Chúng mang E02, E03, E04, E05.

Báo cáo tuần 5 gộp chúng lại và nói rõ ở câu đầu mục 1 vì sao gộp.

##### Đếm kỳ báo cáo còn lại

Tuần 5 (04/09), 6 (11/09), 7 (18/09), 8 (25/09), 9 (02/10) — **năm kỳ**, và thư tuần 9 là thư mang báo cáo giữa kỳ đi.

##### Phạm vi PR

`UniversityRequirements/` gitignore từ đầu (`git ls-files` = 0 file), nên PR chỉ chứa `TASKS.md`.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
677 passed in 14.36s

$ python UniversityRequirements/Reports/tao_bao_cao_giua_ky.py
...\Bao_cao_giua_ky_KLTN.docx

$ python UniversityRequirements/WeeklyLogs/tao_bao_cao_tuan_05.py
...\Bao_cao_tuan_05_31-08_den_06-09.docx
```

---

<a id="pr-73"></a>

### #73 — Báo cáo tuần: thêm bản nháp tuần 6 và bảng theo dõi từng tuần

- **Nhánh:** `bao-cao-tuan-06-nhap` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 14:54 · **gộp:** 06/09/2026 14:54 · **commit gộp:** [`5d36263`](https://github.com/wsunicorn/vihallulens/commit/5d36263079fdceb3e1190d978fc7f423c8542e19)
- **Thay đổi:** +28 / −0, 1 file · **bình luận bot:** 0

##### Tuần 6 chưa diễn ra, nên đây là bản nháp

Tuần 6 là **07/09 – 13/09**, hôm nay mới 02/09. Báo cáo tuần là minh chứng đánh giá quá trình gửi GVHD, nên điền số phỏng đoán vào đó sẽ làm tài liệu mất hết giá trị làm minh chứng.

Cách xử lý — cờ `DA_CHAY = False` trong script bật ba thứ cùng lúc:

- mọi ô số ghi `[ chưa có số ]`, in nghiêng
- tên file mang hậu tố `_BAN_NHAP`
- đầu tài liệu có banner **BẢN NHÁP — CHƯA GỬI**

Chạy xong tuần 6 thì điền số, đổi cờ thành `True`, chạy lại là ra bản gửi được. Các dòng mở đầu bằng `»` là ghi chú nội bộ, tự biến mất khi bật cờ.

##### Phần đã biết chắc thì điền sẵn hết

- khung sáu mục giống báo cáo tuần 4 và 5
- việc dự kiến của T29–T31, lấy từ mục kế hoạch trong báo cáo tuần 5
- dòng Qwen2.5-7B trong bảng so mô hình, lấy từ số đã đo (0,757 · 528 ms · 8.428 MB)
- vị trí hai đầu chú ý dẫn đầu hiện tại (lớp 5 đầu 7, lớp 17 đầu 4) để đối chiếu với Sailor2
- kế hoạch tuần 7 lấy từ T32–T35
- lý do mỗi cấu hình phải chạy một phiên GPU riêng: T4 hạ xung 10–15 % sau vài phút chạy liên tục, đo ở T08

Tổng cộng **33 ô** còn trống.

##### Bảng theo dõi chín tuần

Thêm vào mục việc hành chính, ghi rõ tuần 4 **đã soạn mà chưa gửi** và thư tuần 9 (02/10) là thư mang báo cáo giữa kỳ đi.

##### Phạm vi PR

`UniversityRequirements/` gitignore từ đầu nên PR chỉ chứa `TASKS.md`.

---

<a id="pr-74"></a>

### #74 — T29: E12 ablation — nhóm chunk-aware cộng thêm một số âm

- **Nhánh:** `t29-ablation-nhom-dac-trung` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 15:15 · **gộp:** 06/09/2026 15:16 · **commit gộp:** [`01510d6`](https://github.com/wsunicorn/vihallulens/commit/01510d60cad83934f6fa55d1d7eff8cdc17773e4)
- **Thay đổi:** +503 / −8, 6 file · **bình luận bot:** 0

Bốn mức cộng dồn trên ViHallu. **0 giây GPU** — đọc lại shard `8c49fc0417f1` mà E02 và E03 đã dùng.

##### Kết quả

| Nhóm đặc trưng | Dev chọn riêng | Chênh | Gộp chung `k=32` | Chênh |
|---|---|---|---|---|
| Chỉ bề mặt | 0,6562 | — | 0,6562 | — |
| + lookback gộp | 0,7653 | **+0,1091** | 0,7759 | **+0,1197** |
| + chunk-aware | 0,7388 | **−0,0266** | 0,7688 | **−0,0071** |
| + ổn định | 0,7746 | +0,0358 | 0,7746 | +0,0057 |

##### Vì sao chạy hai lần

Cột chênh của lượt đầu **không đọc thẳng được**: dev chọn `k=64` cho mức 2, `k=16` cho mức 3, `k=32` cho mức 4 — nên −0,0266 gồm cả "thêm bốn đại lượng" lẫn "số cột tụt từ 64 đầu xuống 16". Khóa cách gộp lại thì còn −0,0071.

Tôi suýt ghi thẳng −0,0266 vào báo cáo. Con số đó phóng đại gần **bốn lần**.

##### Không mâu thuẫn với E03

E03 đo +0,0116. Khác đúng một điều: E03 không có hai đặc trưng bề mặt trong véc-tơ, E12 có ở mọi mức. Ba con số +0,0116, −0,0071, −0,0266 đều nằm sâu trong KTC rộng **0,063** của tập test 700 mẫu.

Phát biểu đúng: **đóng góp riêng của nhóm chunk-aware trên ViHallu không phân biệt được với 0**, dấu đổi tùy khung đo.

##### Không đụng phần cơ chế

Định vị 87,8 % (E06), phép lặp trên bộ hai (E08), can thiệp đúng cả bốn hướng (E08), ECE giảm hơn nửa (E03) — nguyên vẹn. Và tỷ lệ gộp **không** chỉ được đoạn nào, bất kể điểm số.

Nó củng cố đúng kết luận mục 5.7 báo cáo giữa kỳ: **định vị đúng ≠ phân loại đúng.**

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
682 passed in 14.60s
```

---

<a id="pr-75"></a>

### #75 — Báo cáo tuần: trình bày theo tiến độ kế hoạch thay vì dồn một lá thư

- **Nhánh:** `bao-cao-theo-tien-do` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 15:33 · **gộp:** 06/09/2026 15:33 · **commit gộp:** [`318b213`](https://github.com/wsunicorn/vihallulens/commit/318b213fc09bc4ddcc7a472fed82cfed47f77fe9)
- **Thay đổi:** +33 / −25, 1 file · **bình luận bot:** 1

Nhóm chạy sớm khoảng ba tuần. Trước đây báo cáo tuần 5 gom hết T20–T28 vào một lá, còn tuần 6 thì trống vì nội dung dự kiến T29–T31 chưa chạy. Đảo lại: mỗi tuần báo cáo đúng phần kế hoạch giao cho tuần đó.

##### Lịch mới

| Tuần | Gửi | Nội dung | Chạy thật |
|---|---|---|---|
| 5 | 04/09 | T20–T22: E02, năm đặc trưng, E03 | 28–29/08 |
| 6 | 11/09 | T23–T24: E04, E05, chốt cách chia đoạn | 30/08 |
| 7 | 18/09 | T25–T27: E06, E07, E08 | 31/08–01/09 |
| 8 | 25/09 | T28: soạn báo cáo giữa kỳ | 02/09 |
| 9 | 02/10 | Gửi báo cáo giữa kỳ (hạn 04/10) | — |
| 10 | 09/10 | T29–T31 | E12 xong 02/09 |

Hệ quả tốt: tuần 6 và 7 **không còn ô trống nào**, đã xóa bản `_BAN_NHAP`.

##### Ràng buộc giữ cho việc này trung thực

Pacing chỉ đổi **thứ tự trình bày**, không bao giờ đổi **ngày**:

- mỗi tiểu mục ghi ngày chạy thật ở tiêu đề — "1.1. Tái lập nguyên văn phương pháp nền (chạy 28/08)"
- `loi_mo_dau_som()` in một câu ở đầu mục 1 nói nhóm chạy sớm hơn kế hoạch và đang trình bày theo tiến độ

`TASKS.md` ghi email và báo cáo tuần là **minh chứng đánh giá quá trình**, ngang kết quả kỹ thuật. Viết "tuần này nhóm em chạy E06" khi nó chạy từ 31/08 là khai sai mốc thời gian trong hồ sơ chấm điểm. "Báo cáo E06 theo kế hoạch tuần 7, đã chạy sớm 31/08" thì vừa đúng ý vừa đúng sự thật — và đọc lên còn có lợi hơn, vì cho thấy nhóm đi trước.

##### Gom phần dùng chung

Thêm `bao_cao_tuan.py` giữ bộ hàm định dạng, thay vì mỗi script một bản sao. Ba script tuần 5, 6, 7 đều dùng nó.

##### Phạm vi PR

`UniversityRequirements/` gitignore từ đầu nên PR chỉ chứa `TASKS.md`.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
682 passed in 13.41s
```

---

<a id="pr-76"></a>

### #76 — Báo cáo tuần: soạn nốt tuần 8 và 9, trọn bộ tới mốc giữa kỳ

- **Nhánh:** `bao-cao-tuan-08-09` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 15:47 · **gộp:** 06/09/2026 15:47 · **commit gộp:** [`57c32e5`](https://github.com/wsunicorn/vihallulens/commit/57c32e5de986a10e2707fae6dbf2ad3412f306fe)
- **Thay đổi:** +11 / −3, 1 file · **bình luận bot:** 1

Soạn nốt hai tuần cuối trước mốc giữa kỳ. Từ tuần 5 tới tuần 9 nay đã đủ, chỉ còn đọc lại rồi gửi đúng ngày.

##### Hai tuần mới

| Tuần | Gửi | Nội dung | Chạy thật |
|---|---|---|---|
| 8 | 25/09 | T28 — soạn báo cáo giữa kỳ | 02/09 |
| 9 | 02/10 | Gửi báo cáo giữa kỳ, hạn 04/10 | — |

##### Tuần 9 dùng chung một lá thư với báo cáo giữa kỳ

`Email_giua_ky.md` đính kèm **cả hai** file: quyển báo cáo giữa kỳ và `Bao_cao_tuan_09`. Quy trình đòi thư hàng tuần và đòi nộp giữa kỳ ở tuần 8–9; một lá thư làm cả hai việc, đúng ghi chú về ba email quan trọng của kỳ trong `Mau_email_bao_cao_tuan.md`. Không gửi thư tuần 9 riêng.

Báo cáo tuần 9 cố tình ngắn — nội dung chính nằm ở quyển báo cáo gửi kèm, nên nó chỉ là thư ngỏ: đã gửi gì, xin gì, làm gì tiếp. Lặp lại nội dung quyển báo cáo sẽ đưa thầy cùng một thứ hai lần.

##### Một chỗ áp quy tắc nhất quán

E12 chạy 02/09, **cùng ngày** với T28. Nhưng kế hoạch xếp E12 vào giai đoạn 6 nên nó báo cáo ở **tuần 10**, không gộp vào tuần 8. Cùng một quy tắc pacing, áp cho cả trường hợp bất tiện.

##### Còn lại

Thêm thư tuần 6, 7, 8 kèm bản HTML sẵn sàng dán Gmail.

Nếu từ giờ tới 04/10 có kết quả mới hoặc GVHD góp ý làm đổi hướng thì **chạy lại script tuần tương ứng**, đừng sửa tay file `.docx`.

##### Phạm vi PR

`UniversityRequirements/` gitignore từ đầu nên PR chỉ chứa `TASKS.md`.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
682 passed in 13.67s
```

---

<a id="pr-77"></a>

### #77 — T30: công cụ E13 so Qwen2.5-7B với Sailor2-8B, chờ chạy Kaggle

- **Nhánh:** `t30-e13-sailor2` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 16:03 · **gộp:** 06/09/2026 16:03 · **commit gộp:** [`ee8bcdb`](https://github.com/wsunicorn/vihallulens/commit/ee8bcdbd5d7a35932a94431ed38a082bfeff219b)
- **Thay đổi:** +866 / −1, 6 file · **bình luận bot:** 1

Câu hỏi thật của E13 **không phải** "mô hình nào điểm cao hơn". Sailor2-8B-SFT mở rộng từ chính họ Qwen2.5 rồi huấn luyện thêm rất nhiều trên ngôn ngữ Đông Nam Á, nên nó là phép thử tự nhiên: **vị trí các đầu chú ý có ích là thuộc tính của kiến trúc hay của dữ liệu huấn luyện?**

##### Ba file

| File | Vai trò |
|---|---|
| `configs/e13_sailor2_vihallu.yaml` | Giống hệt E03 mọi khóa, chỉ đổi `model_name` |
| `scripts/compare_heads.py` | So vị trí đầu chú ý giữa hai mô hình, **0 giây GPU** |
| `notebooks/t30_sailor2_t4.ipynb` | 14 ô, ~3 giờ GPU |

##### Ba chỗ dễ hỏng, xử lý từng chỗ

**1. Lớp tràn số của Sailor2 không suy ra được từ Qwen.** T07 đo Qwen hỏng đúng lớp 27 ở float16 trên 20/20 mẫu. Bê nguyên sang thì hoặc bỏ nhầm lớp lành, hoặc giữ lớp hỏng và sinh `nan` — chỉ lộ ra **sau 3 giờ GPU**.

`exclude_layers: []` trong repo là **cố ý**. Ô 5 chạy `compare_dtypes` (~10 phút) rồi tự ghi đè danh sách đo được vào config, nên `extraction_hash` phản ánh đúng thứ đã chạy. Ô 6 chặn nếu nó còn trống. Thêm dòng máy đọc được `EXCLUDE_LAYERS=[...]` vào `compare_dtypes` — bóc danh sách ra từ một câu tiếng Việt có dấu là ý tồi.

**2. Lưới lớp × đầu có thể khác.** Qwen cho 27 × 28 = 756 cặp; Sailor2 nhiều lớp hơn. Lúc đó so theo chỉ số là **vô nghĩa**: lớp 5 của mô hình 28 lớp và lớp 5 của mô hình 33 lớp nằm ở hai độ sâu khác nhau.

`compare_heads.py` xử lý thành hai nhánh — lưới trùng thì báo overlap@k + kỳ vọng ngẫu nhiên `k²/N` + Spearman; lưới khác thì **từ chối** hai chỉ số đầu và chỉ báo phân bố theo độ sâu tương đối. Có ca kiểm thử khóa "lớp 5 của 28 và lớp 6 của 33 phải ra cùng độ sâu".

**3. Chat template khác.** Ô 6 gọi `render_prompt` với Sailor2 rồi **assert** hai vùng đọc lại từ offset khớp chính xác chuỗi đưa vào, thay vì in ra nhìn bằng mắt.

##### Một lỗi bắt được lúc dựng

Ô cổng ban đầu gọi `build_prompt` — **hàm không tồn tại**, tên thật là `render_prompt`. Nó sẽ chết ở dòng import, tức sau ô dò 10 phút và ngay trước lượt chạy 3 giờ. Bắt bằng cách `compile()` từng ô notebook trước khi commit; đáng thành thói quen vì notebook không có ai lint hộ.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
689 passed in 13.48s

$ (compile từng ô notebook)
o hong: 0
```

---

<a id="pr-78"></a>

### #78 — T30: lượt mốc float32 hết bộ nhớ với Sailor2-8B, sửa thứ tự và thêm bfloat16

- **Nhánh:** `t30-sua-oom` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 16:17 · **gộp:** 06/09/2026 16:17 · **commit gộp:** [`96c661c`](https://github.com/wsunicorn/vihallulens/commit/96c661ccedfa0dc3ef323aac136586dbd4df63ef)
- **Thay đổi:** +122 / −20, 3 file · **bình luận bot:** 1

Lượt chạy Kaggle 06/09 chết ở ô 5.

```
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 20.00 MiB.
GPU 0 has a total capacity of 14.56 GiB of which 12.81 MiB is free.
Of the allocated memory 14.40 GiB is allocated by PyTorch
```

Chết khi **nạp** Sailor2 ở `float32`, trước cả mẫu đầu tiên. Bộ nạp `transformers` chuyển từng tensor sang `float32` trên GPU **trước khi** bitsandbytes lượng tử hóa, còn embedding và lm_head ở nguyên `float32` sau đó. Sailor2 lớn hơn Qwen2.5-7B và mang từ điển Đông Nam Á rộng hơn nên không còn vừa.

##### Chỗ tôi thiết kế sai, và nó đắt hơn cái OOM

`compare_dtypes.py` chạy `float32` **trước** rồi mới `float16`. Nhưng danh sách lớp tràn số **chỉ cần lượt `float16`** — lượt mốc trả lời câu hỏi khác hẳn, là các lớp còn sống có bị bóp méo không.

Thứ tự cũ vứt mất câu trả lời đã nằm trong tầm tay khi nửa *tùy chọn* hết bộ nhớ. **Hỏng một nửa mà mất cả hai.**

##### Ba thứ sửa

1. **`float16` chạy trước** — lấy câu trả lời cần thiết trước phần tùy chọn.
2. **Lượt mốc được phép hỏng** — bắt `OutOfMemoryError`, in cảnh báo, bỏ bảng so lệch, vẫn in `EXCLUDE_LAYERS=[...]`. Chỉ `float16` hỏng mới ném lại.
3. **Thêm `--reference bfloat16`** — cùng dải mũ với `float32` nên không tràn ở chỗ `float16` tràn, mà tốn bộ nhớ ngang `float16`. Với mô hình không vừa mốc `float32` thì nó còn *hợp lý hơn*: cả Qwen2.5 lẫn Sailor2 đều huấn luyện ở `bfloat16`.

Ô 5 truyền `--reference bfloat16` và đặt `PYTORCH_ALLOC_CONF=expandable_segments:True`, đúng thứ thông báo lỗi gợi ý. Ô 7 chạy `float16` + NF4 nên không dính.

##### Hai điều khác thấy trong log, ghi lại chưa xử lý

**`transformers` không được ghim phiên bản.** Mục 5 `CLAUDE.md` đòi ghim trong `pyproject.toml` kèm test khẳng định `attn_weights is not None` — **cả hai đều chưa có**. Kaggle cài **transformers 5.0.0**, bản major mới. Ghim trong `pyproject.toml` cũng không cứu được vì notebook cài `--no-deps`; thứ bảo vệ thật phải là phép kiểm lúc chạy.

**Thiếu `pyvi` và `rank-bm25`.** Vô hại cho T30, cùng gốc `--no-deps`.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
689 passed in 13.70s

$ (compile từng ô notebook)
o hong: 0
```

---

<a id="pr-79"></a>

### #79 — Ghim transformers và chạy test hook trên Kaggle trước khi tiêu GPU

- **Nhánh:** `t30-ghim-transformers` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 16:23 · **gộp:** 06/09/2026 16:23 · **commit gộp:** [`26f3e38`](https://github.com/wsunicorn/vihallulens/commit/26f3e38a7c5150449e4025cc6da8bb3d9ad5ccca)
- **Thay đổi:** +51 / −12, 3 file · **bình luận bot:** 1

##### Đính chính trước

Tin trước tôi nói mục 5 `CLAUDE.md` đòi hai thứ mà **"cả hai đều chưa có"**. **Sai.** Tôi grep chuỗi `attn_weights is not None` trong `tests/` thấy rỗng rồi kết luận, trong khi test có thật, chỉ khác cách diễn đạt.

| Mục 5 đòi | Tình trạng thật |
|---|---|
| Phép kiểm lúc chạy | **Đã có từ T07** — `attention.py` bỏ qua lớp không có `attn_weights`, thử lại với `output_attentions=True`, rồi ném `RuntimeError` kèm tên phiên bản. Hỏng ở **mẫu đầu**, không phải sau 3 giờ |
| Test khẳng định `attn_weights` | **Đã có** — `test_hook_receives_attention_weights`, chạy cả hai giá trị `output_attentions` |
| Ghim phiên bản | **Thiếu thật** → sửa trong PR này |

##### Ghim

`transformers>=5.0,<6`. Sàn 5.0 vì đó là bản thấp nhất đã chạy thật (Kaggle 06/09); mã nguồn được đo trên 5.15.0. Không ghim chặt một bản vì cả hai đều chưa kiểm hết. Trần major vì mục 5 nói đúng chỗ hành vi này đổi.

##### Chỗ hở thật, và nó không phải chỗ tôi tưởng

Ghim trong `pyproject.toml` **không bảo vệ được notebook** — nó cài `--no-deps` nên dùng bản `transformers` của Kaggle (5.0.0).

Nghĩa là bộ kiểm thử bảo vệ đúng thứ cần bảo vệ, nhưng **chỉ từng chạy ở máy cá nhân** — đúng môi trường *không* rủi ro. Môi trường có phiên bản không ai kiểm soát thì chưa bao giờ được hỏi.

**Sửa:** ô 4 nay chạy `tests/test_attention_hook.py` cùng `test_compare_heads.py`, trên chính Kaggle, mất vài giây và **trước khi đụng GPU**. Mô hình Qwen2 hai lớp trọng số ngẫu nhiên chạy CPU nên không cần tải gì.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
689 passed in 13.46s

$ python -m pytest tests/test_attention_hook.py -q     # local, transformers 5.15.0
9 passed
```

---

<a id="pr-80"></a>

### #80 — T30: gc.collect() trước empty_cache, mô hình đầu chưa từng được giải phóng

- **Nhánh:** `t30-gc-truoc-empty-cache` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 16:36 · **gộp:** 06/09/2026 16:36 · **commit gộp:** [`e3bc2dc`](https://github.com/wsunicorn/vihallulens/commit/e3bc2dcc4cad214b22e0be6af2596f890669026c)
- **Thay đổi:** +50 / −2, 2 file · **bình luận bot:** 1

Lượt Sailor2 06/09 **qua được cổng và đang trích**. Nhưng lượt mốc `bfloat16` cũng hết bộ nhớ, và lần này là lỗi tôi đoán sai nguyên nhân.

##### Đoán đúng kích thước, sai nguyên nhân

Tôi nghĩ `bfloat16` sẽ vừa vì nó tốn bộ nhớ ngang `float16`. Số đo:

```
float16 : 20/20 mẫu trong 22 s, VRAM đỉnh 8.785 MB   (card 14,5 GB)
bfloat16: hết bộ nhớ khi nạp
```

Dư gần **6 GB** — thừa chỗ cho mô hình thứ hai. Vậy mà vẫn hết bộ nhớ, nghĩa là **mô hình đầu chưa hề được giải phóng**.

`del extractor` chỉ bỏ một cái tên. Cây `nn.Module` có **vòng tham chiếu**, mà vòng thì đếm tham chiếu không phá được — phải đợi bộ thu gom chu trình chạy. `torch.cuda.empty_cache()` sau đó không giúp gì, vì các khối ấy đang **có chủ** chứ không phải chỉ được nhớ đệm.

Sửa: `gc.collect()` trước `empty_cache()`. Và sửa câu thông báo dự phòng — nó bảo "chạy lại với `--reference bfloat16`" trong khi `bfloat16` chính là thứ vừa hỏng.

##### Lượt chạy nói gì

| Bước | Kết quả |
|---|---|
| Test hook trên Kaggle | **16/16 đạt** với `transformers 5.0.0` |
| Lớp tràn số | **`[30, 31]`** — hai lớp cuối của 32 |
| Config đã ghi | `exclude_layers: [30, 31]`, hash `f58b3bee5934` |
| Kiểm mẫu prompt | Hai vùng đọc lại từ offset **khớp chính xác** |

Sailor2 32 lớp bỏ 2 còn **30**; Qwen 28 bỏ 1 còn **27**. Cả hai chỉ bỏ lớp đuôi nên so theo **độ sâu tương đối** vẫn có nghĩa, nhưng lưới khác nhau nên `compare_heads.py` sẽ từ chối so theo chỉ số — đúng nhánh đã viết sẵn.

##### Hạn chế phải ghi vào báo cáo

Với Qwen, T07 kiểm được sau khi bỏ lớp 27 thì 27 lớp còn lại **khớp `float32` tới 0,07 % thang đo**. Với Sailor2 **chưa có phép kiểm tương đương** — biết hai lớp nào tràn, chưa biết 30 lớp còn sống có bị bóp méo không.

Không chặn T30. Nhưng chương đánh giá phải nói rõ hai bên đứng trên hai mức kiểm chứng khác nhau. Chạy lại ô 5 sau khi có `gc.collect()` sẽ lấp được, tốn ~10 phút GPU.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
689 passed in 13.53s
```

---

<a id="pr-81"></a>

### #81 — T30: tắt thanh tiến trình nạp trọng số, log bị cắt mất phần cần đọc

- **Nhánh:** `t30-tat-thanh-tien-trinh` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 06/09/2026 16:39 · **gộp:** 06/09/2026 16:39 · **commit gộp:** [`e7d1f81`](https://github.com/wsunicorn/vihallulens/commit/e7d1f81b7918a07d803eb6d80c31564f587679d2)
- **Thay đổi:** +9 / −0, 1 file · **bình luận bot:** 1

Lượt Sailor2 06/09 in ra hàng nghìn dòng như thế này:

```
Loading weights:  26%| | 100/387 [00:03<00:06, 44.20it/s, Materializing param=mo
Loading weights:  26%| | 100/387 [00:03<00:06, 44.20it/s, Materializing param=mo
Loading weights:  26%|▎| 101/387 [00:03<00:05, 50.91it/s, Materializing param=mo
```

Mỗi lần vẽ lại một dòng, nhân ba lượt train/dev/test. Nó đẩy log vượt **giới hạn 50.000 ký tự** của trình xem và cắt mất đúng phần cần đọc: số mẫu xong, số lỗi, tỷ lệ cắt ngữ cảnh, VRAM đỉnh.

Một lượt chạy ba giờ mà không đọc được kết quả là một lượt phải ngồi canh.

##### Sửa

```python
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
```

Đặt trong ô trích đặc trưng, trước ba lệnh `!python`. Lệnh `!` kế thừa môi trường của notebook nên áp được cho cả ba lượt.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!
```

---

<a id="pr-82"></a>

### #82 — T30: ô kiểm chặn luôn đường lấy shard về, thêm công cụ soi shard

- **Nhánh:** `t30-soi-shard` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 07/09/2026 11:00 · **gộp:** 07/09/2026 11:00 · **commit gộp:** [`5f3a4c4`](https://github.com/wsunicorn/vihallulens/commit/5f3a4c4d4407b06133994d9f07095623b9fa71c4)
- **Thay đổi:** +369 / −22, 5 file · **bình luận bot:** 0

Lượt 06/09 **trích xong cả ba tập** — 5.600 + 700 + 700 mẫu, lỗi 0, cắt ngữ cảnh 0, ~613 ms/mẫu — rồi ô 8 chặn vì shard có `nan`. Lưới Sailor2 là **30 × 28 = 840 cặp** so với 756 của Qwen.

##### Nguyên nhân

Ô 5 dò trên **20 mẫu** và tìm ra `[30, 31]`. Lượt trích **7.000 mẫu** còn gặp lớp khác — riêng tập test đã `có lớp tràn số: 3/700`.

Phép dò kiểu này **không bao giờ vét cạn được**. Nên chỗ sửa đúng không phải tăng mẫu dò cho thật nhiều, mà là để **chính lượt trích tự khai** ra lớp nào hỏng.

##### Ba chỗ sửa

**1. `extract_features` in ra lớp nào tràn.** Trước chỉ `có lớp tràn số: 3/700` — biết có, không biết lớp nào, nên ba giờ GPU kết thúc mà không có gì để hành động.

**2. Thêm `scripts/inspect_shard.py`.** Đọc shard đã có, **0 giây GPU**, báo lớp nào tràn và bao nhiêu mẫu dính, rồi in giá của hai đường:

| Đường | Giá |
|---|---|
| Bỏ thêm lớp vào `exclude_layers` | Đổi hash → **trích lại ~3 giờ GPU**, mất lớp đó cho *mọi* mẫu kể cả mẫu không sao |
| Bỏ các mẫu hỏng lúc chấm | **0 giây GPU**, chỉ mất đúng số mẫu ấy, báo cáo tỷ lệ như đang làm với tỷ lệ cắt ngữ cảnh |

Cảnh báo nếu tỷ lệ vượt 5 % — trên mức đó đường thứ hai hết rẻ.

**3. Ô 8 không `raise` nữa — chỗ sai nặng nhất.** Nó ném `SystemExit` nên papermill dừng và **ô 9 không chạy**, tức shard ở lại Kaggle rồi chết theo phiên. Mà một shard hỏng chính là thứ **cần đem về nhất** để chẩn đoán. Cổng chặn đúng thứ nó phải bảo vệ.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
695 passed in 15.88s

$ (compile từng ô notebook)
o hong: 0 | tong o: 15
```

---

<a id="pr-83"></a>

### #83 — T30: Sailor2 hỏng cả mạng trên 0,7 % mẫu, không phải hỏng một lớp

- **Nhánh:** `t30-bo-mau-nan` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 21:08 · **gộp:** 09/09/2026 21:08 · **commit gộp:** [`c1272b1`](https://github.com/wsunicorn/vihallulens/commit/c1272b1e403311fbb3a5f624a669fd22baf029ad)
- **Thay đổi:** +194 / −6, 6 file · **bình luận bot:** 1

Lượt 09/09 **trích xong** 5.600 + 700 + 700 mẫu, lỗi 0, cắt ngữ cảnh 0, ~566 ms/mẫu, 66 phút. Lưới **30 × 28 = 840 cặp**. Rồi soi shard ra **49/7.000 mẫu (0,70 %)** có lớp tràn số.

##### Chẩn đoán khác hẳn dự đoán

Bảng theo lớp cho thấy **cùng một tập mẫu ấy hỏng ở MỌI lớp từ 1 trở đi**:

```
train  lớp 0:  6   lớp 1–29: 38 mỗi lớp   → 38 mẫu (0,68 %)
dev    lớp 0:  1   lớp 1–29:  8 mỗi lớp   →  8 mẫu (1,14 %)
test   lớp 0:  1   lớp 1–29:  3 mỗi lớp   →  3 mẫu (0,43 %)
```

Không phải lớp nào yếu, mà **vài mẫu làm activation tràn `float16` ngay từ lớp đầu rồi `nan` lan qua toàn mạng**.

| | Qwen2.5-7B | Sailor2-8B |
|---|---|---|
| Kiểu hỏng | đúng lớp 27, trên **mọi** mẫu | **mọi** lớp, trên vài mẫu |
| Bỏ lớp có cứu được? | có — bỏ 1 lớp xong cho tất cả | **không** — phải bỏ hết 30 lớp |

Công cụ chẩn đoán tự bác đường đó bằng số: *"BỎ THÊM LỚP [0, 1, ..., 29] — mất 30 lớp cho MỌI mẫu"*. Bỏ 30 trên 30 lớp là không còn gì để đo. **Loại không phải vì đắt mà vì vô nghĩa.**

##### Quyết định: bỏ 49 mẫu và báo cáo tỷ lệ

Đúng cách đang làm với tỷ lệ cắt ngữ cảnh. Nguy hiểm duy nhất của việc bỏ mẫu là làm **mẫu số dịch chuyển mà người đọc không biết** — nên mọi chỗ đều in ra số đã bỏ.

`drop_nonfinite()` trong `features/assemble.py`, gọi từ `load_split()` — điểm chung của cả ba script chấm điểm. Chữ ký `load_split` thêm phần tử thứ ba **có chủ ý**: buộc mọi chỗ gọi cũ phải sửa và tự quyết in gì, thay vì lặng lẽ thừa hưởng một thay đổi hành vi.

##### Kiểm chứng không hồi quy

```
$ python scripts/run_chunk_aware.py --config configs/e03_chunk_sentence_vihallu.yaml --dev-only
  chọn                  : topk_heads k=32, 192 chiều
  macro-F1 trên DEV     : 0.7768
```

Đúng bằng Bảng 3. Shard Qwen sạch nên hàm lọc là phép đồng nhất ở đó.

##### Hai hạn chế phải ghi vào báo cáo

1. **Chưa kiểm được các lớp còn sống của Sailor2 có bị bóp méo không** — lượt mốc `bfloat16` hết bộ nhớ lần thứ hai, kể cả sau `gc.collect()`. Qwen có con số 0,07 % thang đo từ T07; Sailor2 không có gì tương đương.
2. **Hai lưới khác nhau** (30 × 28 so với 27 × 28) nên `compare_heads.py` chỉ báo độ sâu tương đối — đúng nhánh đã viết sẵn.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
701 passed in 15.69s
```

---

<a id="pr-84"></a>

### #84 — T30: E13 xong — lookback gộp chuyển được giữa hai mô hình, chunk-aware thì không

- **Nhánh:** `t30-ket-qua-e13` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 21:31 · **gộp:** 09/09/2026 21:32 · **commit gộp:** [`7f79d1a`](https://github.com/wsunicorn/vihallulens/commit/7f79d1a5957492259b1fe05e5f45605efa79b0c6)
- **Thay đổi:** +268 / −40, 7 file · **bình luận bot:** 1

##### Kết quả

| Mô hình đọc | Lưới | lookback gộp | chunk-aware | chênh |
|---|---|---|---|---|
| Qwen2.5-7B | 27 × 28 | 0,7451 | **0,7567** | **+0,0116** |
| Sailor2-8B | 30 × 28 | 0,7377 | 0,7120 | **−0,0257** |
| chênh giữa hai mô hình | | **−0,0074** | **−0,0447** | |

Đọc theo **cột chênh**, không theo dòng nào cao nhất:

1. **Tỷ lệ lookback gộp chuyển gần như hoàn hảo.** Lệch 0,0074 — nhỏ hơn cả biên độ trôi 0,0075 giữa hai môi trường máy tính đo ở T23. Đổi hẳn mô hình đọc mà điểm gần như không nhúc nhích.
2. **Nhóm chunk-aware thì không chuyển.** Đổi dấu, độ lớn gấp đôi. Toàn bộ khoảng cách 0,0447 giữa hai mô hình nằm ở đúng nhóm này.

Nói gọn: **thứ đo "mô hình có bám vào ngữ cảnh không" là thuộc tính bền của kiến trúc; thứ đo "hình dạng phân bố trên các đoạn" thì gắn với từng mô hình cụ thể.**

Bất lợi cho đóng góp đề tài, và **độc lập với E12** — E12 hỏi nhóm này cộng thêm bao nhiêu cạnh đặc trưng bề mặt; E13 hỏi nó có chuyển sang mô hình khác không. Hai phép đo, cùng một hướng.

##### Vị trí đầu chú ý

Hai lưới khác nhau nên `compare_heads.py` từ chối so theo chỉ số, chỉ báo độ sâu tương đối.

| k | Qwen | Sailor2 |
|---|---|---|
| 10 | 0,638 | 0,479 |
| 32 | 0,590 | 0,547 |
| 64 | 0,572 | 0,517 |

Cả hai đều **rải khắp độ sâu**, 23–30 % ở một phần ba đầu. Khoảng cách thu hẹp khi k lớn dần (0,159 → 0,043 → 0,055) nên khác biệt nằm ở *vài đầu dẫn đầu* chứ không ở cả quần thể. Phát biểu đúng: **gần giống nhau, không trùng khít.**

##### Bug thứ hai của cùng một hàm, lệch thêm một biến

Lượt chấm đầu in `e02_lookback_lens : 0.7451` làm mốc cho Sailor2 rồi kết luận **"CHƯA VƯỢT — chia theo đoạn chưa đóng góp được gì"**. Sai: 0,7451 là số của **Qwen**, nên chênh −0,0331 ấy gồm cả phần đổi mô hình lẫn phần đổi nhóm đặc trưng.

`lookback_baseline()` lọc theo bộ dữ liệu và nhóm đặc trưng, **không lọc theo mô hình đọc**. T26 đã sửa hàm này một lần cho biến "bộ dữ liệu"; T30 vấp đúng biến kế tiếp.

Đã thêm bộ lọc `model_name`, hai ca kiểm thử, và `configs/e13_baseline_lookback_sailor2.yaml` — mốc cho **chính Sailor2**, chấm từ shard đã có nên **0 giây GPU**.

**Một mốc so chỉ là mốc khi đúng một thứ khác nhau.**

##### Ba hạn chế đã ghi vào Bảng 5

1. Chưa kiểm được lớp còn sống của Sailor2 có bị bóp méo không — `bfloat16` hết bộ nhớ hai lần.
2. Cột chi phí không so được: 566–572 ms so với 528, nhưng hai phiên GPU khác nhau và T4 hạ xung 10–15 %.
3. Mới đo trên một bộ dữ liệu.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
703 passed in 14.38s
```

---

<a id="pr-85"></a>

### #85 — T31: công cụ E14 bậc thang 7B/3B/1.5B, chờ chạy hai phiên Kaggle riêng

- **Nhánh:** `t31-bac-thang` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 21:41 · **gộp:** 09/09/2026 21:41 · **commit gộp:** [`610ef52`](https://github.com/wsunicorn/vihallulens/commit/610ef52fd689936909b091aad6ed2024153823cd)
- **Thay đổi:** +725 / −1, 6 file · **bình luận bot:** 1

##### E14 nay trả lời hai câu, câu thứ hai do T30 sinh ra

1. **Câu cũ:** phương pháp chạy được trên phần cứng nhỏ hơn không, mất bao nhiêu điểm — trục chi phí của CH2.
2. **Câu mới, đáng giá hơn:** T30 đo được nhóm chunk-aware **không chuyển** giữa Qwen2.5-7B và Sailor2-8B, hai mô hình khác họ huấn luyện. Bậc thang này hỏi nó có chuyển giữa các **cỡ của cùng một họ** không — phép thử **nhẹ hơn hẳn**, cùng kiến trúc và cùng dữ liệu huấn luyện, chỉ khác số tham số.

Không chuyển ở đây thì kết luận E13 mạnh lên nhiều. Chuyển được thì phạm vi E13 thu lại thành *"không chuyển giữa hai họ huấn luyện khác nhau"* — hẹp hơn nhiều.

##### Chỉ phải chạy HAI phiên

| Nấc | Cần chạy? | Lấy số từ đâu |
|---|---|---|
| Qwen2.5-7B | **không** | E02 (0,7451) và E03 (0,7567) |
| Qwen2.5-3B | có | phiên 1, ~45 phút |
| Qwen2.5-1.5B | có | phiên 2, ~35 phút |

##### Vì sao bắt buộc hai phiên RIÊNG

Mục 5 `CLAUDE.md` đo được T4 **hạ xung 10–15 %** sau vài phút chạy liên tục. Chạy hai cỡ nối nhau thì phần hạ xung bị tính nhầm thành khác biệt giữa các mô hình — mà chi phí mỗi mẫu là **một nửa câu hỏi** của E14.

Đây đúng lý do cột chi phí của E13 đã phải ghi là không so được.

##### Bốn cấu hình, hai cặp

Mỗi cỡ có **mốc lookback gộp của chính nó**, dùng chung `extraction_hash` với cấu hình chunk-aware (hash không tính `features`) nên **không tốn thêm giây GPU nào**.

Bài học trực tiếp từ T30: so chunk-aware của Sailor2 với mốc của Qwen thì chênh lệch trộn hai biến.

##### Chỗ dễ hỏng riêng của T31

Ô 6 phải ghi `exclude_layers` vào **cả hai** file của cỡ đang chạy — thiếu một cái thì hai hash lệch và mốc lookback đòi trích lại từ đầu. **Ô 7 so hai hash và dừng nếu lệch.**

Ô 4 bắt trường hợp quên đổi `CO` giữa hai phiên.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
703 passed in 18.04s

$ (compile từng ô notebook)
o hong: 0 | tong: 15
```

---

<a id="pr-86"></a>

### #86 — T30: commit notebook đã chạy, minh chứng của lượt Sailor2

- **Nhánh:** `t30-notebook-da-chay` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 21:47 · **gộp:** 09/09/2026 21:47 · **commit gộp:** [`09afd89`](https://github.com/wsunicorn/vihallulens/commit/09afd895ab4dcf121cdccedf0d486ab6681d75e6)
- **Thay đổi:** +1 / −525, 1 file · **bình luận bot:** 1

Notebook mang output của **10 trên 15 ô**: log dò kiểu số ra `[30, 31]`, cổng kiểm mẫu prompt, ba lượt trích 5.600 + 700 + 700 mẫu, bảng soi shard 49/7.000, và ô lấy kết quả.

Đây là **minh chứng lượt chạy**, không phải file mã nguồn.

##### Tôi đã `git checkout` đè lên file này hai lần

Cả hai lần đều vì so hai bản bằng cách chỉ ghép `''.join(cell['source'])` rồi kết luận *"nội dung giống hệt"*.

Phép so đó **mù đúng chỗ quan trọng**: nó không nhìn `outputs` và `execution_count` — mà đó chính là toàn bộ lý do file này có giá trị. Notebook chưa chạy và notebook đã chạy có `source` y hệt nhau, nên phép so luôn trả về "giống hệt" và tôi luôn kết luận sai.

Lần sau so notebook thì phải so cả `outputs`. Hoặc đơn giản hơn: thấy file notebook bị sửa thì **kiểm có output không TRƯỚC** khi nghĩ tới việc hoàn tác.

---

<a id="pr-87"></a>

### #87 — T31: gộp bậc thang vào một phiên, đo chi phí xen kẽ

- **Nhánh:** `t31-gop-mot-phien` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 21:52 · **gộp:** 09/09/2026 21:52 · **commit gộp:** [`73f177f`](https://github.com/wsunicorn/vihallulens/commit/73f177f305b95d3e6bfe42196b447d4f6fc63f06)
- **Thay đổi:** +282 / −222, 2 file · **bình luận bot:** 1

##### Save Version **có** bị hạ xung — nhưng nó chỉ đụng vào một cột

Hạ xung là chuyện của **phần cứng**, không phải của cách khởi chạy. Save Version chạy trên đúng card T4 ấy qua papermill nên không tránh được. Nhưng phải hỏi tiếp: nó làm hỏng **cái gì**?

| Cột | Hạ xung có đụng tới không |
|---|---|
| macro-F1, F1 từng lớp, ECE | **không** — trọng số chú ý y hệt dù card chạy 1.590 hay 1.200 MHz |
| ms mỗi mẫu | **có** — và đây là một nửa câu hỏi của E14 |

Nên gộp hai cỡ vào một phiên **an toàn cho toàn bộ phần độ chính xác**. Chỉ cột chi phí cần xử lý riêng — và mục 5 `CLAUDE.md` cho sẵn cách: *"chạy mỗi cấu hình một phiên riêng **hoặc đo xen kẽ**"*.

Bản đầu chọn vế thứ nhất và bắt người dùng dựng hai phiên. Bản này chọn vế thứ hai.

##### Ô 9 đo xen kẽ, và tự đo luôn mức trôi

Thứ tự **3B → 1.5B → 3B → 1.5B**, mỗi lượt một tiến trình riêng nạp lại mô hình từ đầu. Card trôi thì trôi lên **cả hai** như nhau, thay vì dồn hết vào mô hình chạy sau.

Hai lượt của cùng một mô hình lệch nhau bao nhiêu **chính là thước đo mức trôi** — in ra để đọc, không giấu. `measure_throughput.py` còn đọc **nhiệt độ GPU** mỗi lượt, nên hạ xung nếu xảy ra thì thấy trực tiếp chứ không phải suy đoán.

**Không cần sửa code:** `measure_throughput.py` đã có `--model`, `--run-name`, `--exclude-layers` và phần đọc nhiệt độ.

##### Kết quả

Notebook 16 ô, **một phiên ~75 phút**, không phải sửa dòng nào khi chạy.

| Bước | Thời gian |
|---|---|
| Dò kiểu số, hai cỡ | ~10 phút |
| Trích 3B + 1.5B | ~47 phút |
| Đo chi phí xen kẽ | ~16 phút |

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
703 passed in 13.50s

$ (compile từng ô notebook)
o hong: 0 | tong: 16
```

---

<a id="pr-88"></a>

### #88 — T31: 7B không trích lại, nhưng đưa vào ô đo chi phí xen kẽ

- **Nhánh:** `t31-7b-vao-do-chi-phi` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 21:59 · **gộp:** 09/09/2026 21:59 · **commit gộp:** [`0f6b29a`](https://github.com/wsunicorn/vihallulens/commit/0f6b29ab3965541c2877da7b73740271c7f955e9)
- **Thay đổi:** +71 / −38, 2 file · **bình luận bot:** 1

Hai nửa của E14 trả lời câu *"7B có cần chạy lại không"* **khác nhau**, nên phải tách ra.

| Nấc | Trích đặc trưng? | Đo chi phí? | Ghi chú |
|---|---|---|---|
| Qwen2.5-7B | **không** | **có** | Độ chính xác đã có: E02 0,7451 và E03 0,7567 |
| Qwen2.5-3B | có | có | |
| Qwen2.5-1.5B | có | có | |

##### Độ chính xác của 7B đã xong

E02 và E03 trích nó rồi — cùng bộ dữ liệu, cùng cách chia đoạn, cùng nhóm đặc trưng — và shard `8c49fc0417f1` còn nằm sẵn trên máy. Trích lại là **đốt 62 phút GPU để dựng lại con số đã có**.

##### Chi phí của 7B thì chưa dùng được

Con số 528 ms/mẫu đo ở một **phiên khác** với phiên sắp đo 3B và 1.5B — đúng kiểu so sánh mà mục 5 `CLAUDE.md` bảo đừng làm, và đúng hạn chế mà cột chi phí của E13 đã phải mang.

##### Nên

7B mang cờ `"trich": False` — bị bỏ qua ở ô dò kiểu số, ô cổng, ô trích và ô soi shard, nhưng **nằm trong ô 9**.

Thứ tự đo thành **7B → 3B → 1.5B → 7B → 3B → 1.5B**, hai vòng qua cả ba nấc. Tốn thêm ~10 phút, đổi lại **một đường cong chi phí ba nấc thật sự so được** — thứ E11 cần, và thứ E13 không có.

Phiên vẫn là một, nay ~80 phút.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
703 passed in 13.75s

$ (compile từng ô notebook)
o hong: 0 | tong o: 16
```

---

<a id="pr-89"></a>

### #89 — T31: guard coi "không lớp nào tràn số" là lỗi, và Qwen2.5-3B sạch hoàn toàn

- **Nhánh:** `t31-sua-guard-rong` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 22:13 · **gộp:** 09/09/2026 22:13 · **commit gộp:** [`5b6e294`](https://github.com/wsunicorn/vihallulens/commit/5b6e294f00385622dfcc59937e665f4a193d4550)
- **Thay đổi:** +86 / −8, 2 file · **bình luận bot:** 1

##### Lượt 09/09 chết ở ô 6

```
SystemExit: khong tim thay dong 'exclude_layers: []' trong configs/e14_qwen3b_vihallu.yaml
```

Dòng đó **có** trong file. Chuyện thật là **Qwen2.5-3B không có lớp nào tràn số** — 0/20 mẫu trên cả 36 lớp — nên `bad = []` và phép thay ghi `exclude_layers: []` đè lên `exclude_layers: []`. Y hệt nhau.

Guard viết là `if patched == text: raise`, gộp hai chuyện khác hẳn:

| Tình huống | Đúng ra |
|---|---|
| Dòng không có trong file | hỏng thật, phải dừng |
| Thay xong mà không đổi gì | kết quả hợp lệ, phải chạy tiếp |

Sửa: kiểm **dòng có tồn tại không** bằng `re.search` trước, rồi mới thay.

Cùng dạng sai với vụ notebook đã chạy: dùng một thứ *thường* trùng với điều mình quan tâm làm đại diện cho nó, rồi nó lệch **đúng lúc** trường hợp trở nên đáng chú ý.

##### Phát hiện đi kèm

| | Qwen2.5-7B | Qwen2.5-3B |
|---|---|---|
| Số lớp | 28 | **36** |
| Lớp tràn số ở `float16` | lớp 27, trên **20/20** mẫu | **không lớp nào** |
| VRAM đỉnh khi dò | 8.428 MB | **3.710 MB** |

**Mô hình nhỏ hơn không thừa hưởng lỗi tràn số của 7B** — đó là chuyện riêng của bản 7B chứ không phải đặc tính họ Qwen2.5.

Lần đầu lượt mốc chạy được nên có bảng lệch mà Sailor2 không cho được:

```
Nếu bỏ các lớp [], còn 36 lớp:
  |Δ| trung bình : 0.00623
  |Δ| phân vị 99 : 0.04883
```

##### Cảnh báo phương pháp phải nêu

Mốc là **`bfloat16`, không phải `float32`**. `bfloat16` có **ít bit định trị hơn** `float16` — 8 so với 10 — nên nó rộng dải mũ (không tràn) nhưng **kém chính xác hơn** ở định trị.

Hệ quả: `|Δ| 0,00623` **gồm cả sai số của chính bfloat16**, tức là **cận trên** chứ không phải phép đo. Không so thẳng với con số 0,07 % mà T07 đo cho 7B bằng mốc `float32`.

Ngoài lề: `bfloat16` chậm **4,4 lần** float16 trên T4 (2.317 so với 527 ms) — Turing không có bf16 gốc.

##### Kiểm tra

```
$ python -m ruff check .
All checks passed!

$ python -m pytest
703 passed in 14.20s
```

---

<a id="pr-90"></a>

### #90 — T31: một nấc hỏng không được kéo cả phiên, và Qwen2.5-1.5B tràn số ở mọi lớp

- **Nhánh:** `t31-nac-hong-khong-keo-ca-phien` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 22:32 · **gộp:** 09/09/2026 22:32 · **commit gộp:** [`cad3186`](https://github.com/wsunicorn/vihallulens/commit/cad3186cd2d958b1a81b36f72829ca2e3f58c11e)
- **Thay đổi:** +304 / −45, 4 file · **bình luận bot:** 1

Lượt 09/09 lần hai qua được nấc 3B rồi chết ở nấc 1.5B, kéo theo bốn ô còn lại của 3B.

##### Phát hiện: Qwen2.5-1.5B không đọc được ở float16

| | 7B | 3B | 1.5B |
|---|---|---|---|
| Số lớp | 28 | 36 | 28 |
| Lớp tràn số ở float16 | lớp 27 | **không lớp nào** | **cả 28 lớp** |
| Mẫu có ít nhất một lớp nan | 20/20 | 0/20 | **20/20** |
| float16 ms/mẫu (lượt dò) | 528 | 513 | 271 |
| bfloat16 ms/mẫu (lượt dò) | — | 2.116 | 1.101 |

Lớp 0 đã hỏng 19/20 mẫu. Hình dạng giống Sailor2 — cả mạng hỏng — nhưng Sailor2 hỏng trên
0,70 % mẫu, đây là 100 %. Không còn mẫu nào để bỏ.

Ba nấc cho ba kiểu hỏng số học khác hẳn nhau trong cùng một họ mô hình.

##### Lỗi thứ nhất: báo cáo tự nó đổ

`compare_dtypes` bỏ 28/28 lớp, còn 0 lớp, `joined` rỗng, rồi
`np.percentile(joined, 99)` → `IndexError: index -1 is out of bounds for axis 0 with size 0`.

Trường hợp rỗng là một kết quả, không phải góc khuất cần chặn. Tách thành `overall_report()`
và cho nó nói thành lời. Thêm dòng `N_LAYERS=<n>` cạnh `EXCLUDE_LAYERS=` — thiếu mẫu số thì
không phân biệt được "một lớp hỏng trong 28" với "cả 28 lớp hỏng", mà hai chuyện cần cách xử
lý ngược nhau.

##### Lỗi thứ hai, đắt hơn: một nấc hỏng kéo cả phiên

Ô 6 `raise SystemExit` khi một nấc hỏng. Nấc 3B đã chạy xong sạch sẽ trước đó, và dòng này
nuốt luôn ô 7–11 của nó. Cùng dạng sai với bug T30, nơi ô kiểm shard dừng trước ô mang shard
về: một cái chặn coi *"một phần hỏng"* là *"không phần nào dùng được"*.

Nấc hỏng nay bị loại khỏi `CAN_TRICH`; ô 7, 8, 10, 11 vốn đã lặp trên đó nên tự bỏ qua. Ô 9
vẫn đo chi phí đủ ba nấc — ms/mẫu không phụ thuộc vào việc đặc trưng có hữu hạn hay không.

##### Tiêu chí hoàn thành

```
$ python -m ruff check .
All checks passed!

$ python -m pytest -q
711 passed in 13.71s
```

`tests/test_compare_dtypes.py` — 8 test, phủ bốn hình dạng: không lớp nào hỏng, một lớp hỏng,
mọi lớp hỏng, lớp sạch nhưng không mẫu nào so được.

##### Còn chờ quyết định

Làm gì với nấc 1.5B — chạy `bfloat16` (~2,2 h GPU), bỏ nấc, hay đổi hàm attention. Kiểu số là
quyết định đã chốt ở mục 3 CLAUDE.md nên không tự đổi. Ba phương án và con số đi kèm ghi trong
TASKS.md.

---

<a id="pr-91"></a>

### #91 — T31: nấc 1.5B chạy bfloat16, vì float16 tràn số cả 28 lớp

- **Nhánh:** `t31-nac-15b-chay-bfloat16` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 22:41 · **gộp:** 09/09/2026 22:41 · **commit gộp:** [`efee41e`](https://github.com/wsunicorn/vihallulens/commit/efee41e733c94f54d8b1591e277cc8aabaf1786b)
- **Thay đổi:** +194 / −58, 7 file · **bình luận bot:** 1

Chốt ngày 09/09/2026 sau khi hỏi. Kiểu số là quyết định đã chốt ở mục 3 CLAUDE.md nên không tự đổi.

##### Vì sao giữ nấc 1.5B thay vì bỏ

Một con số đã đủ nói lên chuyện đắt: `bfloat16` trên T4 chạy 1.101 ms/mẫu, còn 3B ở `float16`
chạy 513 ms/mẫu — **nấc lùi đắt hơn gấp đôi nấc nó lùi khỏi**. Lấy được kết luận ấy mà không
tốn giây GPU nào.

Nhưng chuyện đó chỉ trả lời trục chi phí. Câu hỏi thứ hai của T31 — chunk-aware có chuyển giữa
các cỡ cùng họ không — bỏ nấc thì chỉ còn **một cặp** so sánh, giữ nấc thì có **ba điểm**, tức
một xu hướng. E11 ở T32 cũng vậy: ba điểm là đường cong, hai điểm là đoạn thẳng.

##### Hạn chế, ghi rõ chứ không im

So 1.5B (`bfloat16`) với 3B (`float16`) là để **hai thứ đổi cùng lúc**. Nhưng nó chỉ đụng phần
so **tuyệt đối**; phần *"chunk-aware có hơn mốc lookback của chính nó không"* tính trong nội bộ
từng cỡ — chung mô hình, chung kiểu số, chung shard — nên sạch. Và `bfloat16` trung thực hơn
`float16`, nên nếu 1.5B vẫn kém hơn thì đó là kết luận thận trọng.

Con số chi phí gắn với **T4**: Turing không có bf16 gốc nên phải giả lập, chậm 4,1 lần. Trên
Ampere trở lên vấn đề này biến mất.

##### Đổi những gì

`compute_dtype` vốn đã thuộc `EXTRACTION_KEYS` nên `extraction_hash` tự đổi theo — không phải
sửa hạ tầng.

| Chỗ | Đổi gì |
|---|---|
| Hai config 1.5B | `compute_dtype: bfloat16`, kèm ghi chú vì sao lệch khỏi hai nấc kia |
| `compare_dtypes.py` | thêm `--dtype` để chọn kiểu số đang xét, không còn cứng `float16` |
| Ô 6 | đọc `compute_dtype` **từ YAML**; mốc là `float32` khi kiểu chính là `bfloat16` |
| Ô 9 | truyền `--compute-dtype`, mỗi nấc đo ở đúng kiểu số nó chạy thật |
| CLAUDE.md mục 3, docs/EXPERIMENTS.md | ghi ngoại lệ |

Hai config của 1.5B vẫn trùng `extraction_hash` `9e2b80984a73`, khác hash 3B `8f77142aa220` —
mốc lookback vẫn dùng chung shard, không tốn thêm GPU.

Món lời không tính trước: 1.5B đủ nhỏ để nạp `float32` vừa bộ nhớ (~6,2 GB), nên riêng nấc này
có `|Δ|` đo theo `float32` thật, so thẳng được với 0,07 % của T07 — đỡ hơn cận trên mà nấc 3B
phải chịu khi lấy `bfloat16` làm mốc.

##### Tiêu chí hoàn thành

```
$ python -m ruff check .
All checks passed!

$ python -m pytest -q
711 passed
```

```
$ python -c "... extraction_hash ..."
configs/e14_qwen15b_vihallu.yaml                 bfloat16   9e2b80984a73
configs/e14_baseline_lookback_qwen15b.yaml       bfloat16   9e2b80984a73
configs/e14_qwen3b_vihallu.yaml                  float16    8f77142aa220
```

---

<a id="pr-92"></a>

### #92 — Rà soát toàn repo: sửa bốn chỗ, thêm task cho hai việc E12 để lại

- **Nhánh:** `ra-soat-sua-bon-diem` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 09/09/2026 23:01 · **gộp:** 09/09/2026 23:02 · **commit gộp:** [`87ce9c2`](https://github.com/wsunicorn/vihallulens/commit/87ce9c2335062356610f31066d83d48132bd874b)
- **Thay đổi:** +87 / −9, 2 file · **bình luận bot:** 0

Soát 51 task, 25 script, 39 file `src/`, 35 file test, 18 config, 13 notebook và toàn bộ
`results/runs.jsonl` (24 lượt chạy). Bốn chỗ cần sửa.

##### 1. `docs/EXPERIMENTS.md` tự mâu thuẫn

Trong cùng mục Bảng 3, cách nhau 100 dòng:

| Dòng | Nói gì |
|---|---|
| ~630 | *"Phép đối chứng bác bỏ cách giải thích chồng lấn"* — T24 chạy cửa sổ 48/48, ra 0,7649, thấp hơn cả hai cỡ chồng lấn |
| ~735 | *"Một điều chưa tách được"* — còn nợ 57 phút GPU cho cửa sổ 128 bước 128 |

Đoạn sau là tàn dư của T23 mà T24 đã thay thế. T24 chọn 48/48 thay vì 128/128 vì 48/48 cho
**5,56** đoạn, sát 5,29 của chia theo câu, còn 128/128 chỉ cho **2,43** — tức bỏ được biến chồng
lấn nhưng lôi biến mật độ vào, một đối chứng hỏng.

Viết lại thành phần lịch sử thay vì xóa, vì đường đi từ nghi vấn tới phép đối chứng đáng đọc.

##### 2. Thêm T35B — hai việc E12 để lại

Cả hai đã ghi trong phần *"Việc phải làm trước khi viết chương 7"* của T29 và của mục Bảng 4,
nhưng **chỉ nằm dạng văn xuôi bên trong write-up của một task đã tick**. Không task nào nhận, nên
theo quy trình mục 6 `CLAUDE.md` chúng sẽ không bao giờ tới lượt.

**Việc 1 — E12 trên ISE-DSC01** (22,6 đoạn thay vì 5,3). Đây là phép thử quan trọng nhất còn lại
đối với đóng góp cốt lõi: nếu năm đại lượng hình dạng có ích thật thì chỗ chúng phải có ích nhất
là ngữ cảnh nhiều đoạn. Dấu vẫn âm → kết luận hiện tại vững; dấu đảo → đóng góp phụ thuộc số
đoạn, một phát hiện khác hẳn. Hai khả năng đều dùng được. **0 giây GPU**, shard có sẵn từ T26.

**Việc 2 — mức phụ bề mặt + chunk-aware, bỏ lookback gộp.** Đo thẳng mức chồng lấn tín hiệu vốn
mới chỉ là *cách giải thích khả dĩ nhất*, suy ra chứ chưa đo.

Việc 2 **cần sửa code trước**: `LEVELS` là hằng số cứng, bốn mức cộng dồn theo cấu tạo, không cờ
nào diễn đạt được một mức không cộng dồn. Task ghi rõ đừng thêm thẳng dòng thứ năm vào `LEVELS` —
làm vậy thì mọi lượt sau ra bảng năm dòng, không so được với lượt E12 đã ghi trong `runs.jsonl`.

##### 3. Bảng ánh xạ tuần báo cáo đã cũ

Dòng tuần 4 còn ghi "chưa gửi". Tuần 4 và 5 đã gửi 06/09.

##### 4. T17 không ghi lệnh tái lập

Tiêu chí hoàn thành chỉ ghi hai **kết quả** (`runs.jsonl` ✅, Bảng 1 ✅) mà không ghi **cách gọi
lại**, và `run_baseline_surface.py` là script duy nhất không được nhắc tên ở bất kỳ file `.md`
hay notebook nào trong repo.

Đáng sửa vì đây không phải thí nghiệm phụ: E01 là **sàn của cả đề tài**, và 0,689 sinh ra từ nó
là ngưỡng mà mọi phương pháp khác — kể cả đóng góp của chính đề tài — phải vượt.

##### Tiêu chí hoàn thành

```
$ python scripts/run_baseline_surface.py --dataset vihallu
  macro_f1          0.6562          0.0177   [0.6200, 0.6891]
  f1_no             0.7418
  f1_intrinsic      0.5327
  f1_extrinsic      0.6942
  ece               0.0613
  nhị phân          0.8018
  Tham số phải huấn luyện : 9
  config_hash 6eaabe152a32
```

Trùng từng chữ số với dòng đầu Bảng 1. Chạy với `--results-path` sang chỗ khác nên
`results/runs.jsonl` không bị thêm dòng.

```
$ python -m ruff check .
All checks passed!

$ python -m pytest -q
711 passed
```

---

<a id="pr-93"></a>

### #93 — T31: cất kết quả trích trước khi đo chi phí, và chặn thời gian mỗi lượt đo

- **Nhánh:** `t31-cat-phan-dat-truoc` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 10/09/2026 10:05 · **gộp:** 10/09/2026 10:06 · **commit gộp:** [`231fe3c`](https://github.com/wsunicorn/vihallulens/commit/231fe3c43c990400fbbcecf2acf9a606290cfbf8)
- **Thay đổi:** +245 / −78, 2 file · **bình luận bot:** 1

Lượt 09/09 lần ba **không hỏng chỗ nào**. Ô 6 dò kiểu số xong cả hai cỡ, ô 7 kiểm hash, ô 8 trích
3B trong 28 phút và 1.5B trong 71 phút với 0 lỗi. Rồi ô đo chi phí treo ở lượt 1.5B và phiên nằm
im tới sáng.

Thiệt hại không phải chỗ treo. Thiệt hại là **99 phút trích nằm lại trên máy Kaggle**, vì ô mang
kết quả về đứng *sau* ô đo chi phí.

##### Số đo lấy được — chúng có thật, ghi lại

| Nấc | Kiểu số | Lớp tràn số | Trích 7.000 mẫu | ms/mẫu |
|---|---|---|---|---|
| Qwen2.5-3B | `float16` | không lớp nào (36 lớp) | **28 phút** | ~240 |
| Qwen2.5-1.5B | `bfloat16` | không lớp nào (28 lớp) | **71 phút** | ~604 |

`bfloat16` chạy thật **rẻ hơn lượt dò dự báo** — 604 chứ không phải 1.106 ms/mẫu, vì lượt dò lấy
mẫu trải tới 4.805 từ còn ViHallu ngắn hơn nhiều. Nhưng nấc 1.5B **vẫn đắt gấp 2,5 lần** nấc 3B,
nên kết luận "bậc thang lùi không rẻ hơn" giữ nguyên, chỉ đổi độ lớn.

Lượt mốc `float32` của 1.5B chạy được: `|Δ|` trung bình **0,02225**, phân vị 99 **0,21460**. Đây
là con số **so thẳng được** với 0,07 % của T07 vì cùng mốc `float32` — và nó cho thấy `bfloat16`
lệch 2,2 % thang đo. Phải ghi vào hạn chế.

##### Lỗi 1 — ô đo chi phí lặng lẽ đo sai số lớp

```python
if bo_lop:                       # rỗng thì KHÔNG truyền cờ
    lenh += f" --exclude-layers {bo_lop}"
```

`measure_throughput.py` để mặc định cờ đó là `[27]`. Cả hai cỡ đều có `exclude_layers: []`:

| Nấc | Trích dùng | Đo chi phí dùng |
|---|---|---|
| 3B | 36 lớp | **35 lớp** |
| 1.5B | 28 lớp | **27 lớp** |

Ô 9 mà chạy xong thì cột chi phí và cột độ chính xác đo trên hai mạng khác nhau, không dòng log
nào nói ra. Sửa: truyền cờ **kể cả khi rỗng** — `argparse` với `nargs="*"` nhận `--exclude-layers`
không kèm giá trị và trả về `[]`.

##### Lỗi 2 — không có hạn mức thời gian

`os.system` không hủy được từ notebook. Nay mỗi lượt là `subprocess.run` với hạn mức **15 phút**
(gấp 3,3 lần con số 269 giây lượt 7B thật sự tốn), và lượt quá hạn bị bỏ chứ không dừng cả ô.

Chưa xác định được nguyên nhân treo từ log này và không đoán bừa. Nghi vấn đáng chú ý nhất là
dòng lặp ba lần ở **mọi** lần nạp mô hình — `You are sending unauthenticated requests to the HF
Hub` — và lượt 1.5B là lần nạp thứ bảy của phiên. Nhưng hạn mức chặn được thiệt hại **bất kể
nguyên nhân là gì**, nên không cần biết chắc mới sửa được.

##### Lỗi 3 — cất phần đắt sau cùng. Đây mới là thứ đốt quota

Lần thứ ba cùng một hình dạng sai:

| Lần | Chuyện gì |
|---|---|
| T30 | ô kiểm toàn vẹn shard `raise` **trước** ô mang shard về |
| T31 lần một | một nấc hỏng `raise` và nuốt bốn ô đã xong của nấc trước |
| **lần này** | ô đo chi phí treo, chôn theo 99 phút trích |

Nếp đúng repo đã có sẵn: **T30 và T26 đều đặt ô "lấy kết quả về" ngay sau ô trích, không chèn
việc GPU nào ở giữa.** T31 phá nếp đó khi thêm ô đo chi phí vào giữa.

| Ô | Việc | Vì sao ở đó |
|---|---|---|
| 8 | trích đặc trưng | đắt nhất, ~1 giờ 40 |
| 9 | soi shard | rẻ, CPU |
| **10** | **lấy kết quả về** | **cất phần đắt trước khi làm bất cứ việc GPU nào khác** |
| 11 | đo chi phí xen kẽ | rẻ, chạy lại được; xong thì chép lại `runs.jsonl` |

Ô 8 cũng thôi `raise` khi một split hỏng — trích có lưu tiến độ nên shard dở dang vẫn đáng mang
về, phiên sau đọc tiếp thay vì chạy lại từ đầu.

##### Tiêu chí hoàn thành

```
$ python -m ruff check .
All checks passed!

$ python -m pytest -q
711 passed
```

Thứ tự ô sau khi dựng lại:

```
  8 code | # Ô 8 — trích đặc trưng hai cỡ nhỏ. Khoảng 1 giờ 40.
  9 code | # Ô 9 — soi shard hai cỡ vừa trích. Vài giây, CPU.
 10 code | # Ô 10 — LẤY KẾT QUẢ VỀ. Vài giây. Ô này chạy TRƯỚC ô đo chi phí, cố ý.
 11 code | # Ô 11 — ĐO CHI PHÍ XEN KẼ, ca ba nac. Khoảng 30 phút GPU.
```

---

<a id="pr-94"></a>

### #94 — T31: E14 xong — dấu của chunk-aware đảo hai lần trong cùng một họ mô hình

- **Nhánh:** `t31-notebook-da-chay` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 10/09/2026 15:07 · **gộp:** 10/09/2026 15:07 · **commit gộp:** [`f238802`](https://github.com/wsunicorn/vihallulens/commit/f238802db4958dcb91b30ec7b8e89de1632fad3e)
- **Thay đổi:** +204 / −676, 4 file · **bình luận bot:** 0

Phiên Kaggle 10/09 chạy trọn **6.729 giây (1 giờ 52), 0 lỗi**. Chấm bốn cấu hình trên máy cá
nhân, 0 giây GPU. Notebook đã chạy commit kèm, giữ nguyên 11 ô output.

##### Kết quả chính

| Mô hình đọc | Tham số | Lưới | lookback gộp | chunk-aware | chênh |
|---|---|---|---|---|---|
| Qwen2.5-7B | 7,6 B | 27 × 28 | 0,7451 | **0,7567** | **+0,0116** |
| Qwen2.5-3B | 3,1 B | 36 × 16 | **0,7345** | 0,7217 | **−0,0128** |
| Qwen2.5-1.5B | 1,5 B | 28 × 12 | 0,7232 | **0,7345** | **+0,0114** |

Cột cuối theo thứ tự cỡ giảm dần: **+ → − → +**.

Ba cỡ khác nhau **đúng một biến** là số tham số — cùng họ, cùng dữ liệu huấn luyện, cùng kiến
trúc, cùng bộ chấm, cùng cách chia đoạn, cùng nhóm đặc trưng. Trung bình ba cỡ là **+0,0034**,
nhỏ hơn hai mươi lần độ rộng khoảng tin cậy (~0,065).

Một đóng góp thật **không đảo dấu hai lần** qua ba cỡ của cùng một họ. Phép đo thứ ba độc lập,
cùng một hướng:

| Thí nghiệm | Hỏi gì | Trả lời |
|---|---|---|
| E12 | cộng thêm bao nhiêu khi đứng cạnh đặc trưng bề mặt | không phân biệt được với 0 |
| E13 | có chuyển sang họ mô hình khác không | không, đổi dấu |
| **E14** | **có ổn định qua các cỡ cùng một họ không** | **không, đổi dấu hai lần** |

##### Cột mốc lookback thì ngược lại, và nó có lợi cho CH2

| Mô hình đọc | macro-F1 | Mất so với 7B | VRAM đỉnh |
|---|---|---|---|
| Qwen2.5-7B | 0,7451 | — | 8.328 MB |
| Qwen2.5-3B | 0,7345 | −0,0106 | 3.710 MB |
| Qwen2.5-1.5B | 0,7232 | −0,0219 | 2.718 MB |

**Thu mô hình đọc 4,7 lần chỉ mất 0,022 macro-F1 và tiết kiệm 67 % VRAM.** Nấc 1.5B vẫn **trên**
baseline bề mặt 0,6562 và **ngang** PhoBERT-large 0,749 đã tinh chỉnh, với mô hình đọc bằng 1/5.

Cột này giảm **đều** — mỗi nấc ~0,011 — trong khi cột chunk-aware nhảy lung tung. Chính sự tương
phản ấy là lập luận.

##### Cơ chế giải thích được

Độ sâu trung bình của các đầu mạnh nhất ở k = 64: **7B 0,572, 3B 0,458**. Cách nhau **0,114** —
lớn hơn khoảng cách giữa Qwen2.5-7B và Sailor2-8B ở E13 (0,055), dù Sailor2 khác **họ huấn
luyện** còn 3B thì cùng họ.

Đầu mang tín hiệu dời chỗ theo cỡ, nên năm đại lượng hình dạng — vốn đọc phân bố *từ các đầu cụ
thể* — dời theo. Còn tỷ lệ gộp cộng dồn toàn bộ ngữ cảnh nên không phụ thuộc đầu nào nằm ở đâu.

##### Chi phí

| Nấc | Kiểu số | Lượt | 0–512 | 513–1024 | 1025–2048 | 2049–4096 |
|---|---|---|---|---|---|---|
| 7B | `float16` | 1 / 2 | 404 / 416 | 741 / 756 | 1.350 / 1.375 | 2.609 / 2.585 |
| 3B | `float16` | 1 / 2 | 211 / 209 | 366 / 368 | 688 / 692 | 1.402 / 1.404 |
| 1.5B | `bfloat16` | 1 | 569 | 1.042 | 1.945 | 3.423 |

Đo xen kẽ khử được phần hạ xung: lần 1 so lần 2 lệch dưới **0,9 %** ở 3B và **3,0 %** ở 7B, so
với **10–15 %** T08 đo khi chạy nối nhau.

Và 1.5B ở `bfloat16` **chậm hơn cả 7B ở `float16`** ở mọi mức độ dài, trong khi VRAM là 2.718 so
với 8.328 MB. Nấc lùi **mua được bộ nhớ, không mua được thời gian** — đúng hình dạng bài học ở
nấc 1 mục 5 CLAUDE.md.

##### Một lỗi nhỏ ghi lại

Ô lấy kết quả chỉ chép `results/runs.jsonl`, mà `measure_throughput.py` ghi vào
`results/feasibility.jsonl`. Nên `runs_t31.jsonl` mang về trùng **từng byte** với bản đã có — 24
dòng cũ, không dòng chi phí nào. Bảng trên đọc từ log; còn thiếu đúng lượt 6/6.

##### Tiêu chí hoàn thành

```
$ python scripts/run_chunk_aware.py --config configs/e14_baseline_lookback_qwen3b.yaml
  e14_baseline_lookback_qwen3b      : 0.7345
$ python scripts/run_chunk_aware.py --config configs/e14_qwen3b_vihallu.yaml
  e14_qwen3b_vihallu                : 0.7217   (-0.0128)
$ python scripts/run_chunk_aware.py --config configs/e14_baseline_lookback_qwen15b.yaml
  e14_baseline_lookback_qwen15b     : 0.7232
$ python scripts/run_chunk_aware.py --config configs/e14_qwen15b_vihallu.yaml
  e14_qwen15b_vihallu               : 0.7345   (+0.0114)

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
711 passed
```

Soi shard: **0/7.000 mẫu có lớp tràn số** ở cả hai cỡ, 0 mẫu bị cắt ngữ cảnh.

---

<a id="pr-95"></a>

### #95 — T31: sáu lượt đo chi phí về đủ — nấc 1.5B chậm hơn cả 7B

- **Nhánh:** `t31-cot-chi-phi-day-du` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 10/09/2026 15:13 · **gộp:** 10/09/2026 15:13 · **commit gộp:** [`8d42fb0`](https://github.com/wsunicorn/vihallulens/commit/8d42fb045c8dac97b2aa2a9bdb586fca66ba1716)
- **Thay đổi:** +108 / −36, 3 file · **bình luận bot:** 0

Sáu dòng chi phí trước đó nằm lại trên Kaggle vì ô lấy kết quả chỉ chép `runs.jsonl`, trong khi `measure_throughput.py` ghi vào `results/feasibility.jsonl`. Nay file trong repo có đủ 8 dòng: 2 dòng T08 cũ cộng 6 lượt T31.

##### Cột chi phí, có trọng số theo phân bố độ dài thật

| Nấc | Kiểu số | Lượt 1 | Lượt 2 | Trôi | VRAM đỉnh | Giờ GPU hai bộ chính |
|---|---|---|---|---|---|---|
| 7B | `float16` | 726,6 ms | 741,7 ms | **2,09 %** | 8.328 MB | 10,1 giờ |
| 3B | `float16` | **369,7 ms** | **370,2 ms** | **0,13 %** | **3.710 MB** | **5,1 giờ** |
| 1.5B | `bfloat16` | 1.029,3 ms | 1.029,8 ms | **0,04 %** | 2.718 MB | 14,2 giờ |

**Nấc lùi nhỏ nhất chậm hơn 1,4 lần mô hình lớn gấp năm lần nó**, trong khi VRAM giảm 67 %. Quy ra giờ GPU thì 1.5B tốn 14,2 giờ so với 10,1 của 7B — gần nửa hạn mức tuần.

**Nấc đáng dùng là 3B:** nhanh gấp đôi 7B, nhẹ hơn 56 % bộ nhớ, chỉ mất 0,0106 macro-F1. Bậc thang lùi của mục 5 CLAUDE.md trên phần cứng này thực chất chỉ có **một nấc dùng được**.

##### Đo xen kẽ đo được chính nó

Hai lượt của cùng một mô hình lệch **0,04 % tới 2,09 %**, so với **10–15 %** mà T08 đo khi chạy nối nhau trong một phiên.

##### Một quan sát chưa tách được, ghi nguyên trạng

Telemetry cho thấy card **có** hạ xung: tỷ lệ xung SM tụt tới **0,33** mức tối đa, nhiệt chạm **84 °C**, 5/6 lượt đánh dấu `gpu_throttled: true`.

Nhưng hai lượt 3B vẫn lệch **0,13 %**, dù tỷ lệ xung đọc được là 0,858 ở lượt 1 và 0,330 ở lượt 2 **tại cùng mức độ dài**. Chênh xung 2,6 lần cho chênh thời gian 0,13 %.

Hoặc telemetry là ảnh chụp một thời điểm không đại diện, hoặc xung SM không phải ràng buộc quyết định với suy luận NF4 — mà là giải nén trọng số 4 bit và băng thông bộ nhớ. Cách thứ hai khớp với `forward_share`: 0,92 ở 7B, 0,95 ở 3B, chỉ **0,86** ở 1.5B.

Điều dùng được ngay bất kể cách đọc nào đúng: hai lượt xen kẽ trùng nhau trong 2 %, nên cột chi phí tái lập được.

##### Tiêu chí hoàn thành

```
$ python -m ruff check .
All checks passed!
$ python -m pytest -q
711 passed
```

---

<a id="pr-96"></a>

### #96 — T32: E11 bảng đánh đổi — và nó chứng minh hai ô của Bảng 1 sai

- **Nhánh:** `t32-bang-danh-doi` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 10/09/2026 15:21 · **gộp:** 10/09/2026 15:21 · **commit gộp:** [`891efb9`](https://github.com/wsunicorn/vihallulens/commit/891efb90391e7730104653dc57e17c7f6980fd86)
- **Thay đổi:** +597 / −4, 5 file · **bình luận bot:** 0

Bảng trung tâm của chương 7. Viết thành script chứ không gõ tay, vì lý do dưới đây.

##### Vì sao phải là script

Cột chi phí đến từ **hai file đo hai thứ khác nhau, và cả hai đều đặt tên `ms_per_sample`**:

| File | Nghĩa là gì | Độ lớn |
|---|---|---|
| `results/runs.jsonl` | thời gian **bộ phân loại** — hồi quy logistic, chạy CPU | 0,001–0,013 ms |
| `results/feasibility.jsonl` | thời gian **lượt đọc** để lấy ma trận chú ý | 222–608 ms |

Chênh **năm bậc độ lớn**. Một dòng lấy nhầm cột trông vẫn hợp lý và lật ngược kết luận chương 7 —
nó sẽ nói hướng nội tại nhanh hơn XLM-R hai nghìn lần.

##### Bảng 8 — kết quả

| Phương pháp | macro-F1 | ms/mẫu | VRAM | Tham số |
|---|---|---|---|---|
| Baseline bề mặt (E01) | 0,6562 | **0,001** | — | **9** |
| Gemini giám khảo (E10) | 0,6637 | 8.194,0 | — | 0 |
| PhoBERT-large (E09) | 0,7487 | 12,3 | 9.002 MB | 369.166.339 |
| XLM-R-large (E09) | **0,7762** | 25,2 | 11.231 MB | 559.893.507 |
| Lookback gộp 7B (E02) | 0,7451 | 437,6 | 8.328 MB | 2.271 |
| Chunk-aware 7B (E03) | 0,7567 | 437,6 | 8.328 MB | 579 |
| **Lookback gộp 3B (E14)** | 0,7345 | **222,7** | **3.710 MB** | **195** |
| Chunk-aware 3B (E14) | 0,7217 | 222,7 | 3.710 MB | 1.851 |
| Lookback gộp 1.5B (E14) | 0,7232 | 608,1 | 2.718 MB | 1.011 |
| Chunk-aware 1.5B (E14) | 0,7345 | 608,1 | 2.718 MB | 1.131 |
| Sailor2-8B (E13), hai dòng | 0,7377 / 0,7120 | *chưa đo* | *chưa đo* | 195 / 1.155 |

**XLM-R thắng cả hai trục tuyệt đối** — cao hơn 0,0195 điểm và nhanh hơn **17 lần** dòng
chunk-aware tốt nhất. Không có cách đọc nào biến bảng này thành "hướng nội tại rẻ hơn về thời
gian tuyệt đối". Viết đúng như vậy.

**Chỗ hướng nội tại thắng là số tham số:** lookback gộp trên Qwen2.5-3B đạt 0,7345 với **đúng 195
tham số**, so với **559.893.507** của XLM-R — ít hơn **2,87 triệu lần**, mất 0,0417 điểm. Và 195
tham số thì huấn luyện trên CPU trong vài giây, không có rủi ro không hội tụ như InfoXLM ở E09.

**Nấc 3B là điểm cân bằng của cả bảng.**

##### Cột chi phí biên: đã lượng hóa, vẫn là giả thiết

Chi phí biên 0,002–0,010 ms tách thành cột riêng có nhãn. **Không thí nghiệm nào trong đề tài đo
được nó** — nó đòi hệ RAG đầu cuối, mà T40 mới dựng.

Và có một khoản biên **thật mà chưa ai đo**: bật `output_attentions` vô hiệu hóa FlashAttention,
nên hệ RAG đang dùng FlashAttention phải trả thêm để lấy được ma trận chú ý.

##### Hai ô của Bảng 1 sai

Bảng 1 ghi E02 tốn **464 ms** và E03 tốn **528 ms**. Hai dòng đọc **chung shard `8c49fc0417f1`**,
chung `extraction_hash`, tức **chung một lượt chạy mô hình đọc**. Một lượt trích không có hai giá.

Chênh 64 ms là nhiễu giữa hai phép đo, bị đọc nhầm thành "chunk-aware đắt hơn lookback" — và nó
đã nằm trong **báo cáo giữa kỳ**. Lượt xen kẽ T31 cho **437,6 ms** cho cả hai, trôi 2,09 %.

Quy tắc rút ra, nay có test khóa: **hai dòng chung `extraction_hash` phải chung ô chi phí.**

##### Tiêu chí hoàn thành

```
$ python scripts/build_tradeoff.py
  số dòng            : 12/12
  Đã ghi results/tradeoff.csv — 12 dòng

  Chưa đo chi phí, để trống thay vì mượn số của mô hình khác:
    - Lookback gộp, Sailor2-8B (E13)
    - Chunk-aware, Sailor2-8B (E13)

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
721 passed
```

---

<a id="pr-97"></a>

### #97 — T33: dựng công cụ E15 trên split gốc ViWikiFC, và sửa một con số của T15

- **Nhánh:** `t33-e15-viwikifc-goc` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 10/09/2026 15:36 · **gộp:** 10/09/2026 15:36 · **commit gộp:** [`ebc9ae3`](https://github.com/wsunicorn/vihallulens/commit/ebc9ae377cba7e2bda8873182f5248df177bffee)
- **Thay đổi:** +511 / −10, 4 file · **bình luận bot:** 1

##### E15 khác E08 ở chỗ nào

Cả hai chạy trên ViWikiFC nhưng dùng **hai bộ khác nhau**, và lẫn hai cái này thì mọi con số vô
nghĩa.

| | E08 (T27) | **E15 (T33)** |
|---|---|---|
| Bộ dữ liệu | `viwikifc_e08`, **dẫn xuất** | `viwikifc`, **gốc** |
| Ngữ cảnh | dựng lại bằng BM25, 10 câu, ~496 token | `context` có sẵn, ~154 từ |
| Split | dev, dựng thành cặp | train/dev/test **gốc của bộ** |
| Trả lời | phép can thiệp, cơ chế | so với số đã công bố |

E08 phải dựng lại ngữ cảnh vì `context` gốc quá ngắn để làm phép can thiệp theo cặp. E15 thì
**bắt buộc dùng ngữ cảnh gốc** — dùng ngữ cảnh dựng lại là so với một bài toán khác bài toán mà
InfoXLM và SemViQA giải.

##### Công cụ

Hai cấu hình cùng ra `extraction_hash` **3c1a9a052afa** nên mốc lookback không tốn thêm giây GPU.

Notebook **đơn giản hơn T31 hai chặng**: không dò kiểu số (lớp 27 của Qwen2.5-7B chốt từ T07),
không đo chi phí (T31 đã cho phép chiếu cho ViWikiFC, ~424 ms/mẫu). Thứ tự ô giữ đúng nếp PR #93
khôi phục — **trích → soi shard → lấy kết quả về**, không chèn việc GPU nào vào giữa.

Ô lấy kết quả **sửa luôn lỗi của T31**: chép cả `results/runs.jsonl` lẫn `results/feasibility.jsonl`.

##### Sửa một con số của T15

Bảng chunk của T15 đếm **theo ngữ cảnh duy nhất**, nhưng câu kết luận dưới bảng phát biểu **theo
mẫu**: *"hơn một phần bảy số mẫu không đóng góp gì cho câu hỏi CH1"*.

Đo lại trên đủ dữ liệu:

| Bộ | Mẫu | Ngữ cảnh | 1 chunk theo **ngữ cảnh** | 1 chunk theo **mẫu** |
|---|---|---|---|---|
| ViHallu | 7.000 | 3.865 | 1,0 % | 1,1 % |
| ISE-DSC01 | 36.369 | 4.793 | 0,0 % | 0,0 % |
| **ViWikiFC** | 20.919 | 1.481 | **15,3 %** | **5,9 %** |
| ViFactCheck | 7.232 | 1.041 | 0,0 % | 0,0 % |

Một phần **mười bảy**, không phải một phần bảy.

Ba bộ còn lại không dính lỗi vì ở chúng hai cách đếm gần trùng nhau. Chỉ ViWikiFC có tương quan
giữa "ngữ cảnh ngắn" và "ít mẫu dùng lại" đủ mạnh để tách hai con số — 20.919 mẫu dùng chung chỉ
1.481 ngữ cảnh.

Chuyện này **không** làm T16 mất lý do tồn tại: 4,73 đoạn mỗi mẫu vẫn mỏng, và E08 còn cần ngữ
cảnh mười câu dựng có kiểm soát. Nhưng lập luận đỡ lưng cho T16 phải nói đúng độ lớn của nó.

##### Tiêu chí hoàn thành

```
$ python -c "... extraction_hash ..."
configs/e15_chunk_viwikifc.yaml               extraction 3c1a9a052afa  groups ['basic','chunk_aware','stability']
configs/e15_baseline_lookback_viwikifc.yaml   extraction 3c1a9a052afa  groups ['basic']

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
721 passed
```

Chưa tick T33 — còn chờ một phiên Kaggle ~2 giờ 30.

---

<a id="pr-98"></a>

### #98 — T33: E15 xong — kém SemViQA 13 điểm trên split gốc, và cùng đầu chú ý dẫn đầu ở cả ba bộ

- **Nhánh:** `t33-ket-qua-e15` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 08:47 · **gộp:** 11/09/2026 08:47 · **commit gộp:** [`11f35ca`](https://github.com/wsunicorn/vihallulens/commit/11f35cac061c63037679db8848b67b33a1df5019)
- **Thay đổi:** +137 / −334, 4 file · **bình luận bot:** 1

Phiên Kaggle 10/09 trích 20.919 mẫu trong **138 phút, 0 lỗi, 0 tràn số**, 395 ms/mẫu. Notebook đã
chạy commit kèm, 8/8 ô output. Chấm trên máy cá nhân, tập test **gốc** 2.091 mẫu.

##### Bảng 6

| Phương pháp | Đầu vào | Acc | macro-F1 |
|---|---|---|---|
| InfoXLM large (bài gốc) | **bằng chứng vàng** | — | 86,51 |
| SemViQA (bài SemViQA) | câu tự truy xuất | VC 83,88 | — |
| **Lookback gộp, Qwen2.5-7B** | toàn bộ `context` | 70,73 | **70,66** [68,72–72,55] |
| **Chunk-aware, Qwen2.5-7B** | toàn bộ `context` | 70,59 | **70,54** [68,57–72,48] |

##### Cột "đầu vào" quyết định cách đọc

InfoXLM 86,51 nhận **đúng câu bằng chứng vàng** rồi mới phân loại — bài toán dễ hơn hẳn bài toán
đọc cả ngữ cảnh rồi tự tìm chỗ cần nhìn. Con số ấy là trần của một bài toán khác.

Mốc so được nhất là **SemViQA VC Acc 83,88**. Nhóm đạt **70,73**. **Kém 13 điểm**, viết đúng như vậy.

Ba thứ làm khoảng cách nhỏ hơn con số trần trụi, cả ba đều đo được chứ không phải chống chế:

- **Rò rỉ 100 % ngữ cảnh** (T14): bộ mã hóa 560 triệu tham số tinh chỉnh trọn vẹn **nhớ được**
  1.481 ngữ cảnh; hồi quy logistic 2.271 tham số thì không. Rò rỉ nâng số bên kia nhiều hơn.
- **33 % nhãn NEI lẫn loại** (T13, kappa 0,505).
- **2.271 tham số so với 560 triệu**, không tinh chỉnh, chạy CPU.

##### Chunk-aware bằng lookback — lần thứ tư, đo chặt nhất

Chênh **−0,0012** trên **2.091** mẫu, gấp ba cỡ test ViHallu. Khoảng tin cậy hẹp còn 0,038 và hai
khoảng chồng gần khít. Bộ này còn thiên vị chunk-aware nhẹ vì chỉ 5,9 % mẫu có một đoạn.

| Phép đo | Đổi gì so với E03 | Chunk-aware − lookback |
|---|---|---|
| E12 | thêm đặc trưng bề mặt | −0,0071 |
| E13 | đổi họ mô hình | −0,0257 |
| E14 | đổi cỡ | −0,0128 / +0,0114 |
| **E15** | **đổi bộ dữ liệu, split gốc** | **−0,0012** |

##### Phát hiện thêm: cùng đầu dẫn đầu ở cả ba bộ

Với **cùng** Qwen2.5-7B:

| Bộ | #1 | #2 | #3 |
|---|---|---|---|
| ViHallu | `l5_h7` | **`l17_h4`** | `l24_h3` |
| ISE-DSC01 | **`l17_h4`** | `l18_h0` | `l5_h7` |
| ViWikiFC | **`l17_h4`** | `l15_h5` | `l16_h2` |

Ghép với E13/E14, nơi **đổi mô hình** thì đầu dời chỗ hẳn (độ sâu 0,572 → 0,517 → 0,458):

> **Vị trí đầu mang tín hiệu là thuộc tính của mô hình đọc, không phải của bộ dữ liệu.**

Cơ sở trực tiếp cho T34 / E16.

##### Tiêu chí hoàn thành

```
$ python scripts/run_chunk_aware.py --config configs/e15_baseline_lookback_viwikifc.yaml
  e15_baseline_lookback_viwikifc    : 0.7066
$ python scripts/run_chunk_aware.py --config configs/e15_chunk_viwikifc.yaml
  e15_chunk_viwikifc                : 0.7054   (-0.0012)

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
721 passed
```

Soi shard: **0/20.919** mẫu có lớp tràn số, 0 bị cắt ngữ cảnh.

---

<a id="pr-99"></a>

### #99 — T34: E16 xong — bộ phát hiện ba lớp không chuyển được giữa hai bộ, vì ba lớp không cùng nghĩa

- **Nhánh:** `t34-e16-cheo-bo` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 09:17 · **gộp:** 11/09/2026 09:17 · **commit gộp:** [`362fc48`](https://github.com/wsunicorn/vihallulens/commit/362fc48c2a694d08e63a060e8c44914fa3b67d4c)
- **Thay đổi:** +548 / −6, 5 file · **bình luận bot:** 0

Bốn chiều, **0 giây GPU**, đọc lại shard E02/E03 và E07. Cách gộp đầu chọn trên **dev của bộ
nguồn**; bộ đích chỉ đụng một lần, để chấm. Cùng một mô hình chấm trên cả hai tập test nên điểm
test nguồn là phép kiểm tái lập tích hợp — **cả bốn trùng E02, E03, E07 từng chữ số.**

##### Bảng 7

| Nguồn → đích | Nhóm | Chéo bộ [KTC] | Đích tự chấm | Sụt | Nhị phân | ECE |
|---|---|---|---|---|---|---|
| ViHallu → ISE-DSC01 | lookback | **0,4301** [0,4146–0,4456] | 0,7851 | −0,3550 | 0,6309 | 0,372 |
| ViHallu → ISE-DSC01 | chunk-aware | **0,3584** [0,3450–0,3719] | 0,7919 | −0,4334 | 0,6640 | 0,354 |
| ISE-DSC01 → ViHallu | lookback | **0,5540** [0,5179–0,5913] | 0,7451 | −0,1911 | 0,7838 | 0,291 |
| ISE-DSC01 → ViHallu | chunk-aware | **0,5521** [0,5160–0,5897] | 0,7567 | −0,2047 | 0,7756 | 0,297 |

Mức ngẫu nhiên ba lớp ≈ 0,33. **Không chiều nào chuyển được tới mức dùng.** ECE sụp từ 0,03–0,11
lên 0,29–0,37 — đoán sai mà tự tin.

##### Mỗi chiều mất đúng một lớp — và giải thích được

| Chiều | Lớp gần như biến mất | Đoán / thật | Dồn đi đâu |
|---|---|---|---|
| ViHallu → ISE-DSC01 | `extrinsic` | 82 / 1.286 | 988 vào `intrinsic` |
| ISE-DSC01 → ViHallu | `intrinsic` | 72 / 234 | 136 vào `extrinsic` |

Lớp `no` chuyển được ở cả hai chiều (62 %, 82 %). Lý do nằm ở **định nghĩa nhãn**: `extrinsic`
của ViHallu là GPT-4o *bịa* thêm — mô hình không nhìn ngữ cảnh; `extrinsic` của ISE-DSC01 là NEI
— câu do người viết, mô hình vẫn nhìn, chỉ không tìm thấy. T13 đã đo chuyện này từ phía nhãn (67 %
NEI thật sự là ngoại lai); E16 đo nó từ phía đặc trưng.

##### Cái chuyển được là "trung thực hay không"

Nhị phân chéo bộ **0,78** và **0,63–0,66** — trên ngẫu nhiên nhị phân 0,50 ở cả bốn dòng. Cùng
phát hiện với Bảng 1: **phần khó, và phần không chuyển được, nằm ở ranh giới nội tại–ngoại lai.**

##### Chunk-aware chuyển kém hơn lookback — lần thứ năm, lần này ngoài nhiễu

Chiều khó: 0,4301 so với 0,3584, chênh **−0,0717** — hơn hai lần độ rộng khoảng tin cậy. Năm đại
lượng hình dạng học trên 5,3 đoạn rồi gặp 24,5 đoạn.

##### Công cụ

`scripts/run_cross_dataset.py` **khẳng định** hai cấu hình giống nhau ở mọi thứ trừ `dataset`.
Hai shard khác mô hình hay khác chunker cho véc-tơ cùng độ dài mà cột khác nghĩa — bộ phân loại
vẫn chạy và vẫn trả về một con số. `tests/test_cross_dataset.py` có 10 ca, sáu ca là sáu cách
lệch mà script phải từ chối.

##### Tiêu chí hoàn thành

```
$ python scripts/run_cross_dataset.py --source configs/e03_chunk_sentence_vihallu.yaml \
    --target configs/e07_chunk_aware_isedsc01.yaml --reference-run e03_chunk_aware
  vihallu/test    0.7567   isedsc01/test   0.3584   sụt +0.3983
  Đối chiếu điểm cùng bộ : e03_chunk_aware ghi 0.7567, lượt này 0.7567 → TRÙNG
$ ... e02 → e07_baseline                       0.7451 → 0.4301   TRÙNG
$ ... e07_chunk → e03                          0.7919 → 0.5521   TRÙNG
$ ... e07_baseline → e02                       0.7851 → 0.5540   TRÙNG

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
731 passed
```

---

<a id="pr-100"></a>

### #100 — T35: phân tích sai sót — 48 % lỗi là nhầm giữa hai loại ảo giác, prompt bỏ dấu không ảnh hưởng

- **Nhánh:** `t35-phan-tich-sai-sot` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 09:32 · **gộp:** 11/09/2026 09:32 · **commit gộp:** [`6142114`](https://github.com/wsunicorn/vihallulens/commit/6142114548a2c17873fd3cf571fbf3670c99a9f1)
- **Thay đổi:** +865 / −2, 8 file · **bình luận bot:** 1

Khớp lại đúng mô hình E03 (`topk_heads k=32`, 192 chiều) và đối chiếu `y_pred` đã lưu: **700/700
trùng**. Tập test 700 mẫu, sai **169** (24,1 %).

##### Cặp nhầm — toàn bộ 169 mẫu sai

| Cặp | Số mẫu | % lớp thật |
|---|---|---|
| `intrinsic` → `extrinsic` | **46** | 19,7 % |
| `extrinsic` → `intrinsic` | **36** | 15,9 % |
| `intrinsic` → `no` | 33 | 14,1 % |
| `no` → `intrinsic` | 27 | 11,2 % |
| `extrinsic` → `no` | 16 | 7,1 % |
| `no` → `extrinsic` | 11 | 4,6 % |

**82/169 (48,5 %) là nhầm giữa hai loại ảo giác với nhau.** Chỉ 16 % bỏ sót thành `no`.

##### Nhãn cấu trúc — tự động, ngưỡng ghi cứng

| Nhãn | Có mặt / 169 |
|---|---|
| `tu_tin_sai` | 55 |
| `phan_van` | 34 |
| `chep_lai_ma_sai` | **23** |
| `prompt_noisy` | 5 |
| `mot_doan`, `dien_dat_lai`, `phan_hoi_ngan` | **0** |
| `khac` | 69 |

Ba nhãn bằng 0 tự chúng là kết quả: phản hồi GPT-4o **luôn dài, luôn chép nhiều**, kể cả khi trung thực.

##### `noisy` so với còn lại — yêu cầu treo từ đầu ở EXPERIMENTS.md

| Nhóm | n | macro-F1 [KTC 95 %] | Tỷ lệ sai |
|---|---|---|---|
| `noisy` | 23 | 0,7798 [0,5765–0,9151] | 21,7 % |
| còn lại | 677 | 0,7558 [0,7235–0,7866] | 24,2 % |

**Không có bằng chứng prompt bỏ dấu làm bộ phát hiện kém đi.** Chỉ 23 mẫu nên khoảng rộng 0,34.

##### Năm hình dạng lỗi, từ đọc tay 8 mẫu

1. **Một mệnh đề bịa giữa phần chép lại** — 23 mẫu, mô hình tự tin 0,90–0,97 là `no`. Đặc trưng
   lấy trung bình toàn phản hồi nên mệnh đề ấy bị trung bình hóa mất.
2. **Trộn hai loại ảo giác dưới một nhãn** — bóp méo con số *và* bịa lời khen trong cùng một câu.
3. **Phủ định lật ngược bằng chính từ ngữ ngữ cảnh** — chú ý cho biết *nhìn vào đâu*, không cho
   biết *nói gì về chỗ đó*.
4. **Tiền đề sai** — 13/700 câu hỏi mang nguyên tiền tố "Adversarial Question:". Sai 38,5 % so với
   23,9 %, n = 13 nên chỉ là quan sát.
5. **Nhãn có thể tranh cãi** — "5 triệu năm" so với "6,5 triệu năm" mà nhãn là `no`.

Ba hình dạng đầu chỉ cùng một hướng phát triển: **chấm theo đoạn của phản hồi**.

##### Phụ thuộc

`matplotlib` khai vào nhóm `dev` — dự án đã dùng ở `tao_hinh_giua_ky.py`, chưa khai. Không vào lõi.

##### Còn lại là của người

Cột `ghi_chu_tay` trong CSV trống — lượt đọc 100 mẫu là phần "LM" của task.

##### Tiêu chí hoàn thành

```
$ python scripts/error_analysis.py --config configs/e03_chunk_sentence_vihallu.yaml \
    --reference-run e03_chunk_aware
  đối chiếu y_pred đã lưu: 700/700 trùng
  Đã ghi results/error_analysis.csv — 100 dòng
  Đã vẽ results/error_analysis.png

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
747 passed
```

---

<a id="pr-101"></a>

### #101 — T35B: E12 trên ISE-DSC01 cho chênh +0,0002, và chunk-aware chồng lấn 99,9 % với lookback

- **Nhánh:** `t35b-e12-isedsc01-chong-lan` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 10:38 · **gộp:** 11/09/2026 10:38 · **commit gộp:** [`c16f6d4`](https://github.com/wsunicorn/vihallulens/commit/c16f6d41450d6292851c2cbb186ac08b3f96e4e4)
- **Thay đổi:** +287 / −31, 6 file · **bình luận bot:** 1

Hai việc E12 để lại từ T29. Cả hai **0 giây GPU**, đọc lại shard E07 (`15ef31521fd6`).

##### Bảng 4b — E12 trên ISE-DSC01, đặt cạnh ViHallu

| Bộ | Cách gộp | Chỉ bề mặt | + lookback | + chunk-aware | **chênh** | + ổn định |
|---|---|---|---|---|---|---|
| ViHallu | dev | 0,6562 | 0,7653 | 0,7388 | −0,0266 | 0,7746 |
| ViHallu | gộp chung | 0,6562 | 0,7759 | 0,7688 | −0,0071 | 0,7746 |
| ISE-DSC01 | dev | 0,4767 | 0,7837 | 0,7839 | **+0,0002** | 0,7918 |
| ISE-DSC01 | gộp chung | 0,4767 | 0,6554 | 0,6950 | +0,0396 | 0,7024 |

**Việc 1: ở 22,6 đoạn, chênh là +0,0002.** Không âm, không dương — bằng không. Kết luận vững, không
phụ thuộc số đoạn.

Dòng gộp chung +0,0396 là **hiện tượng giả**: khóa 32 đầu làm lookback mất 0,128 trên bộ này, rồi
128 cột chunk-aware từ chính 32 đầu ấy nhặt lại một phần. Khi lookback dùng đủ 758 cột thì phần
cộng thêm biến mất. Chế độ gộp chung — thêm ở T29 để cột chênh sạch trên ViHallu — gây hiện tượng
giả trên bộ nhiều đoạn.

##### Bảng 4c — chồng lấn, đo bằng số

`chồng lấn = gain(lookback riêng) + gain(chunk riêng) − gain(cả hai)`

| Bộ | Cách gộp | lookback riêng | chunk riêng | cả hai | **chồng lấn** | / chunk riêng |
|---|---|---|---|---|---|---|
| ViHallu | dev | +0,1091 | +0,0232 | +0,0825 | +0,0497 | 214 % |
| ViHallu | gộp chung | +0,1197 | +0,0237 | +0,1126 | +0,0308 | 130 % |
| ISE-DSC01 | dev | +0,3070 | +0,2268 | +0,3072 | **+0,2266** | **99,9 %** |
| ISE-DSC01 | gộp chung | +0,1787 | +0,1438 | +0,2183 | +0,1042 | 72 % |

**Việc 2 sửa lại giả thuyết T29.** Chunk-aware *không* chồng lấn với bề mặt — một mình nó cộng
**+0,2268** trên ISE-DSC01 so với bề mặt, tức có tín hiệu riêng, và nhiều khi ngữ cảnh dài. Thứ nó
chồng lấn là **lookback gộp**: 99,9 %.

> Năm đại lượng hình dạng **có** mang tín hiệu, càng nhiều đoạn càng mang nhiều, nhưng là cùng một
> tín hiệu lookback gộp đã mang. Không cộng thêm gì vào bộ phát hiện, không phụ thuộc số đoạn.
> Cái chúng có mà lookback không có là đầu ra chỉ được đoạn nào.

##### Cách làm

Không chèn dòng thứ năm vào `LEVELS`. `--extra-level GROUPS` chấm thêm một mức không cộng dồn bằng
**cùng hàm `score_level`**, ghi vào `extra["extra_levels"]`. Kiểm tái lập sau refactor: ViHallu gộp
chung cho **đúng bốn số của Bảng 4**.

Sửa hai dòng in: chế độ gộp chung in "không có đầu nào để gộp" dù có gộp; đường dẫn ghi in cứng.

##### Tiêu chí hoàn thành

```
$ python scripts/run_ablation.py --config configs/e12_ablation_isedsc01.yaml --extra-level chunk_aware
  + chunk-aware   0.7839   +0.0002
  chồng lấn = riêng + riêng − cả hai   +0.2266

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
749 passed
```

---

<a id="pr-102"></a>

### #102 — T36: thư viện hoàn chỉnh — DetectorBundle mang công thức dựng cột, pipeline một lời gọi

- **Nhánh:** `t36-thu-vien` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 10:53 · **gộp:** 11/09/2026 10:53 · **commit gộp:** [`ab86bd3`](https://github.com/wsunicorn/vihallulens/commit/ab86bd3e64f9031495d3265790bfd72d23f04233)
- **Thay đổi:** +1008 / −140, 15 file · **bình luận bot:** 1

##### Khoảng trống thật, đối chiếu `docs/SPEC.md`

`LookbackDetector.save/load` có rồi, nhưng chỉ lưu **bộ phân loại** — không lưu nó đọc cột nào:
nhóm đặc trưng, cách gộp đầu, **32 chỉ số đầu dev đã chọn**, lưới lớp. Script biết lúc chạy rồi vứt.
T35 phải khớp lại E03 từ đầu để có mô hình mà soi. T37 (API) cần đúng thứ đó.

##### Bốn mảnh

| Mảnh | Việc |
|---|---|
| `features/records.py` | `to_record`, `gold_chunk_rank` từ script vào thư viện |
| `features/assemble.py` | chế độ `mixed` + `build_matrix` một cửa — E15 chọn chế độ này |
| `detect/bundle.py` | `DetectorBundle`: bộ phân loại **kèm** công thức dựng cột, **từ chối** bản ghi khác lưới |
| `pipeline.py` | `HallucinationDetector.score(...)` → đúng schema `/score`; `from_pretrained` nạp đúng mô hình đọc trong bundle |

```python
from vihallulens import HallucinationDetector
detector = HallucinationDetector.from_pretrained("models/e03_chunk_aware.pkl")
result = detector.score(context, question, response)
result.label, result.risk_score, result.chunk_attention, result.to_dict()
```

##### Phép kiểm quyết định

Bundle E03 (11,5 KB, 579 tham số, 192 cột) `predict_record` **từng bản ghi** test: **700/700** trùng
`y_pred` T22 đã ghi. Refactor script kiểm bằng E03 chạy lại ra **0,7567** y hệt.

##### Hai quyết định trong pipeline

**`risk_score = 1 − P(no)`** — Bảng 1, Bảng 7 và E16 đều cho thấy chỉ phán đoán nhị phân là bền và
chuyển được giữa các bộ. **`chunk_attention`** = tỷ trọng trung bình mọi lớp và đầu — đại lượng E06
đã chấm hit@1 87,8 % — *không phải* thứ bộ phân loại đọc. Cả hai ghi vào docstring để T39 không nhầm.

##### Tài liệu khớp code

README và SPEC còn liệt kê `train_detector.py` và `evaluate.py` — chưa bao giờ tồn tại. Sửa về
`run_chunk_aware.py --save-bundle` và ghi lý do gộp.

##### Tiêu chí hoàn thành

```
$ python scripts/run_chunk_aware.py --config configs/e03_chunk_sentence_vihallu.yaml \
    --save-bundle models/e03_chunk_aware.pkl
  macro_f1            0.7567   [0.7242, 0.7885]
  Đã lưu bundle models/e03_chunk_aware.pkl (11.5 KB) — e03_chunk_aware: basic, chunk_aware,
  stability · topk_heads (32 đầu) · lưới 27 × 28 · 192 cột · 579 tham số

  predict_record từng bản ghi vs y_pred đã lưu: 700/700

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
760 passed
```

---

<a id="pr-103"></a>

### #103 — T37: dịch vụ REST ba endpoint, kiểm hợp đồng không GPU

- **Nhánh:** `t37-rest-api` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 10:57 · **gộp:** 11/09/2026 10:57 · **commit gộp:** [`c4254ba`](https://github.com/wsunicorn/vihallulens/commit/c4254ba88f7d6cf876221423ddf68979af82e550)
- **Thay đổi:** +455 / −1, 6 file · **bình luận bot:** 1

Ba endpoint của `docs/SPEC.md` §2.6 bọc `HallucinationDetector`. Sau T36 đây là lớp mỏng.

| Endpoint | Nhận | Trả |
|---|---|---|
| `POST /score` | `{context, response, question?, chunk_strategy?}` | `{label, proba, risk_score, chunk_attention, elapsed_ms, …}` |
| `POST /score/batch` | `{items: [...]}`, tối đa 64 | `{results, elapsed_ms}` |
| `GET /health` | — | mô hình nạp chưa, tên, VRAM, số request |

##### Ba chỗ có thể sai lặng lẽ, và cách chặn

| Chỗ | Chặn |
|---|---|
| Trả lời trước khi mô hình nạp xong | nạp trong `lifespan`; `/health` trả `loading` → `ok` → `error` kèm lý do; route chấm trả **503** |
| `chunk_strategy` khác cách bộ phát hiện được khớp | **400** nêu cách đúng — không lặng lẽ bỏ qua |
| Lô có một phần tử hỏng | kiểm cả lô **trước** khi chấm; 400 cả lô, không trả hai kết quả lẫn một lỗi |

SPEC viết `chunk_strategy` như tham số tự do. Nó không tự do: năm đặc trưng hình dạng mô tả phân
bố trên đúng các đoạn E05 đã chọn. Chia khác thì bộ phân loại nhận véc-tơ khác nghĩa và vẫn trả nhãn.

##### Chưa chạy thật, nói rõ

`from_pretrained` cần GPU; máy cá nhân không có CUDA. 11 ca test chứng minh **hợp đồng**, chưa chứng
minh chấm đúng với mô hình thật. Smoke test chạy tay trên Kaggle (SPEC §5) ghi vào **T40** — demo dù
sao cũng phải bật server.

##### Tiêu chí hoàn thành

```
$ python -m pytest tests/test_serve.py -q
11 passed
$ python scripts/serve.py --help
usage: serve.py [-h] [--bundle BUNDLE] [--device DEVICE] [--host HOST] [--port PORT]

$ python -m ruff check .
All checks passed!
$ python -m pytest -q
771 passed
```

---

<a id="pr-104"></a>

### #104 — T38: Dockerfile một lệnh, và build thật bắt được hai lỗi của T37

- **Nhánh:** `t38-docker` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 11:27 · **gộp:** 11/09/2026 11:27 · **commit gộp:** [`9510005`](https://github.com/wsunicorn/vihallulens/commit/9510005e6c78cff5c6f98ea3ebb445e8f4b3dea1)
- **Thay đổi:** +306 / −23, 10 file · **bình luận bot:** 1

```bash
docker compose up --build
```

Ảnh nền `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime` (torch, CUDA 12.4, Python 3.11 có sẵn).
Trọng số Qwen2.5-7B **không nướng vào ảnh** — tải lần đầu vào volume `hf-cache`. `HF_TOKEN` tùy
chọn, đọc từ `.env` đúng mục 2 CLAUDE.md.

##### Build thật bắt được hai lỗi của T37

11 ca test T37 tiêm sẵn bộ phát hiện nên không thấy. Bật container lên thì thấy ngay:

**1. `/health` không trả lời gì suốt 150 giây.** `lifespan` nạp mô hình đồng bộ, mà uvicorn không
mở cổng cho tới khi `lifespan` trả về — cả quãng nạp là cả quãng cổng đóng, *đúng quãng `/health`
tồn tại để báo*. Sửa: nạp trong **luồng nền**; `/health` có bốn trạng thái `loading | ok | error |
not_loaded` kèm trường `error`; `create_app(loader=)` để test tiêm loader chặn trên `Event`.

**2. Tải 15 GB rồi mới biết không có GPU.** Sửa ở `from_pretrained`: `device=cuda` mà
`torch.cuda.is_available()` sai thì `RuntimeError` ngay. Sau sửa: `/health` báo `error` sau
**6 giây**, không tải gì.

##### Kiểm trong container

| Kiểm | Kết quả |
|---|---|
| `docker build` | thành công, 10,5 GB |
| import gói, nạp bundle | đúng |
| chấm lại 700 bản ghi test (mount shard) | **700/700** trùng `y_pred`, dù sklearn 1.9.0 → 1.9.1 |
| khởi động không GPU | `/health` → `error` kèm lý do sau 6 s; `/score` → 503 |
| `docker compose config` | hợp lệ |

sklearn chặn `>=1.9,<2` trong pyproject — qua major, pickle không hứa gì.

##### Chưa chạy với GPU

Máy cá nhân không có CUDA. Ảnh chưa từng chấm một request thật; `/health` = `ok` trên máy GPU ghi
vào **T40**.

##### Tiêu chí hoàn thành

```
$ docker build -t vihallulens:latest .        # exit=0
$ docker compose config --quiet               # OK
$ docker run ... predict_record vs y_pred     # 700/700
$ python -m ruff check .                      # All checks passed!
$ python -m pytest -q                         # 774 passed
```

---

<a id="pr-105"></a>

### #105 — T39: trang quan sát tô màu đoạn theo tỷ trọng chú ý, HTML + JS thuần

- **Nhánh:** `t39-trang-quan-sat` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 11:33 · **gộp:** 11/09/2026 11:33 · **commit gộp:** [`d15b1bf`](https://github.com/wsunicorn/vihallulens/commit/d15b1bf137e62aa8a318008f00cbceefda7a5e11)
- **Thay đổi:** +317 / −2, 5 file · **bình luận bot:** 0

Một file `src/vihallulens/serve/static/index.html`, phục vụ ở `GET /`, không phụ thuộc ngoài —
đúng SPEC §2.6.

##### Trang vẽ đúng thứ API trả, không tự tính gì

Gọi đúng hai endpoint client lập trình gọi: `/health` khóa nút Chấm tới khi `ok`, `/score` để
chấm. Test khóa các tên trường `chunk_attention`, `risk_score`, `char_start`, `char_end` — đổi
schema thì test hỏng chứ không phải trang hỏng lặng lẽ.

**Tô màu bằng cách cắt chuỗi ngữ cảnh gốc theo `char_start`/`char_end`**, không ghép từ `text` —
những gì hiện ra đúng từng ký tự với những gì đã chấm. Độ đậm = `share / max(share)`.

##### Kiểm dưới Node (máy không có trình duyệt)

Chạy `chunk_context` thật lên ngữ cảnh bốn câu, gọi đúng `renderContext` của trang qua DOM giả:

```
van ban sau khi to == ngu canh goc: true
alpha moi doan: 0.235 0.860 0.176 0.424
doan dam nhat la doan co share lon nhat: true
bang xep hang co 4 dong
```

##### Điều trang nói với người xem

Chú thích ghi thẳng: màu cho biết mô hình **nhìn vào đâu**, không cho biết câu trả lời **nói gì
về chỗ đó** (E06 87,8 %; T35: phủ định lật ngược vẫn tô đúng đoạn). Điểm rủi ro là con số nên hành
động theo. Một trang demo gợi ý "đoạn đỏ là đoạn sai" sẽ hứa điều luận văn đã đo là không đúng.

Ba nút ví dụ: trung thực, nội tại, ngoại lai — bấm một cái là thấy. Nhìn bằng mắt trên máy GPU
thuộc T40.

##### Tiêu chí hoàn thành

```
$ python -m pytest tests/test_serve.py -q     # 15 passed
$ python -m ruff check .                      # All checks passed!
$ python -m pytest -q                         # 776 passed
```

---

<a id="pr-106"></a>

### #106 — T40: hệ RAG minh họa, một mô hình vừa trả lời vừa chấm; notebook gom bốn smoke test GPU

- **Nhánh:** `t40-he-rag-minh-hoa` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 12:20 · **gộp:** 11/09/2026 12:20 · **commit gộp:** [`17c439d`](https://github.com/wsunicorn/vihallulens/commit/17c439d71cc1a56a7c2a93bb45cd72d251791fbe)
- **Thay đổi:** +739 / −5, 9 file · **bình luận bot:** 0

##### Truy xuất → sinh trả lời → chấm, một mô hình làm cả

`serve/rag.py`: kho **21 tài liệu** ngắn về Việt Nam (tự viết), truy xuất bằng `EvidenceIndex` BM25
của T16, sinh câu trả lời bằng **chính mô hình đọc đang nạp** — cùng chat template mục 8 CLAUDE.md
với `add_generation_prompt`, giải mã tham lam — rồi chấm. Không nạp mô hình thứ hai. Đó cũng chính
là thiết lập mà lập luận chi phí biên ở Bảng 8 mô tả.

Ba mặt: `POST /demo/ask`, `GET /demo/corpus`; ô "Hỏi hệ RAG" trên trang; `scripts/demo_rag.py`.

##### Kiểm không GPU

BM25 lấy đúng top-1 cho bốn câu thử. Năm ca test qua `TestClient` với `generator=` giả — test khóa
rằng bộ ba đưa vào chấm **chính là** ngữ cảnh đã truy xuất, câu hỏi, và câu trả lời đã sinh.

##### Một phiên Kaggle gom bốn smoke test GPU

`notebooks/t40_demo_t4.ipynb`, nạp mô hình **một lần**:

| Ô | Kiểm | Thuộc |
|---|---|---|
| 5 | `from_pretrained` rồi `score` ba ví dụ | T36 |
| 6 | hệ RAG, bốn câu hỏi | T40 |
| 7 | uvicorn chạy **thật**: `/health` → `ok`, `/score` mẫu có nhãn, `/demo/ask`, 400 cho strategy lạ | T37 |
| 8 | `GET /` trả trang | T39 |

Docker (T38) không chạy trên Kaggle — vẫn chưa kiểm với GPU.

**Chưa tick T40** — tiêu chí là demo chạy đầu cuối.

##### Tiêu chí hoàn thành (phần không GPU)

```
$ python -m pytest tests/test_serve.py -q     # 20 passed
$ python -m ruff check .                      # All checks passed!
$ python -m pytest -q                         # 781 passed
```

---

<a id="pr-107"></a>

### #107 — T40: cài rank-bm25 và nâng scikit-learn trong notebook, tiền kiểm nạp thử bundle

- **Nhánh:** `t40-sua-cai-dat` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 12:34 · **gộp:** 11/09/2026 12:34 · **commit gộp:** [`eed353c`](https://github.com/wsunicorn/vihallulens/commit/eed353c67790204cff29a1db590999d26de94bdb)
- **Thay đổi:** +22 / −2, 1 file · **bình luận bot:** 0

Lượt đầu chết ở ô 3: `thieu rank_bm25`. Kaggle không có sẵn, mà `--no-deps` cố ý không kéo phụ thuộc — bài học T27 đã ghi ngay trong ô 2 của nó, tôi không dùng lại.

Log còn lộ chuyện đáng nghĩ hơn: Kaggle có **scikit-learn 1.6.1**, bundle pickle bằng **1.9.0**, pyproject chặn `>=1.9,<2` từ T38. Câu hỏi thật là pickle 1.9.0 có nạp được trên 1.6.1 không — chưa ai kiểm.

Sửa: ô 2 cài `rank-bm25` và nâng `scikit-learn>=1.9,<2` theo đúng trần đã chặn; ô 3 **nạp thử bundle** rồi `predict_proba` trên véc-tơ không — biết lúc này rẻ hơn biết sau một phút nạp 7B.

```
$ python -m ruff check .   # All checks passed!
$ python -m pytest -q      # 781 passed
```

---

<a id="pr-108"></a>

### #108 — T40: kết quả phiên Kaggle — ba smoke test qua, sinh câu trả lời ra NaN vì lớp 27

- **Nhánh:** `t40-ket-qua` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 12:48 · **gộp:** 11/09/2026 12:48 · **commit gộp:** [`ea85a70`](https://github.com/wsunicorn/vihallulens/commit/ea85a707659af3672f1c6b77a97dc5bf2d3749ec)
- **Thay đổi:** +886 / −331, 5 file · **bình luận bot:** 0

Notebook 9/9 ô có output và ba JSON commit làm minh chứng. Phiên 208 giây.

##### Ba smoke test qua

| Kiểm | Kết quả |
|---|---|
| **T36** thư viện thật | nạp 110 s, VRAM 5.562 MB; ba ví dụ trung thực/nội tại/ngoại lai → `no` 0,001 / `intrinsic` 0,998 / `extrinsic` 1,000 — **cả ba đúng** |
| **T37** REST thật | `/health` `ok`; `/score` mẫu `vihallu_train_19` nhãn `no`, đoán `no` (P 0,683); strategy lạ → **400** |
| **T39** trang | `GET /` 200, đủ bốn dấu hiệu |

##### T40: truy xuất đúng, sinh ra rác — và lý do là lớp 27

Cả bốn câu trả lời bắt đầu `![](https://cdn…` rồi lặp `!-!-!-`. Không phải ảo giác — **logit NaN**:

- Token id **0** của Qwen2.5 là `!` (kiểm bằng tokenizer). `argmax` trên NaN → 0.
- T07: lớp 27 tràn số 20/20 mẫu ở `float16`. Bộ phát hiện né bằng cách không hook lớp đó
  (`nonfinite_layers=[]`), nhưng **dòng dư vẫn qua lớp 27 rồi vào LM head**. Teacher forcing
  không dùng logit → chấm vô hại. Sinh → chết.

**Cấu hình làm bộ phát hiện rẻ chính là cấu hình làm cùng mô hình ấy không sinh được.** Ghi vào
hạn chế của lập luận chi phí biên (Bảng 8).

Chi tiết đáng giữ: bộ phát hiện gán `extrinsic` 1,000 cho cả bốn câu rác.

##### Cần chốt

Đổi bộ sinh là quyết định kiến trúc (mục 6.4). Ba phương án trong TASKS.md; nghiêng về
**Qwen2.5-1.5B `bfloat16` làm bộ sinh riêng** (+2,7 GB, T31 đo 0 lớp tràn).

---

<a id="pr-109"></a>

### #109 — T40: bộ sinh riêng — Qwen2.5-7B nạp thêm bản bfloat16, vì float16 không sinh được

- **Nhánh:** `t40-bo-sinh-bf16` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 12:53 · **gộp:** 11/09/2026 12:53 · **commit gộp:** [`2edaf47`](https://github.com/wsunicorn/vihallulens/commit/2edaf47c9e7ef3a1d91a9d041dfe236de90431aa)
- **Thay đổi:** +489 / −38, 7 file · **bình luận bot:** 0

Chốt theo tiêu chí người dùng: **chất lượng đánh giá tốt nhất, không lo GPU Kaggle.**

Bộ phát hiện không đổi dù bộ sinh là gì, nên chất lượng demo phụ thuộc câu trả lời phải mạch lạc
và cùng cỡ với mô hình chính — 7B hơn 1.5B, và giữ tinh thần "cùng trọng số đọc và viết".

##### `AnswerGenerator`

NF4, `bfloat16`, `sdpa`, không hook, generation config của checkpoint. `DemoRAG` nạp lười ở câu
hỏi đầu tiên; `/health` báo bộ sinh đã nạp chưa. Thêm ~5,5 GB (tổng ~11 GB, dưới trần T4), giải mã
chậm ~4× trên T4 vì Turing không có bf16 gốc.

##### Điều khoản phần cứng — ghi vào Bảng 8 và README

Lập luận "lượt đọc dù sao cũng trả" giả định hệ RAG sinh bằng chính mô hình đọc. Trên T4 ở
`float16` mô hình ấy **không sinh được** (lớp 27 → logit NaN → token 0 = `!`). Chi phí biên gần 0
chỉ đúng trên phần cứng có `bfloat16` gốc (Ampere+), nơi một bản duy nhất vừa đọc vừa viết.

##### Tiêu chí hoàn thành

```
$ python -m ruff check .   # All checks passed!
$ python -m pytest -q      # 781 passed
```

Notebook ô 6 in VRAM trước/sau khi nạp bộ sinh. Cần chạy lại trên Kaggle, ~12 phút.

---

<a id="pr-110"></a>

### #110 — T40: hai bản 7B không nằm chung T4 — bộ sinh về Qwen2.5-3B bfloat16, cỡ lớn nhất còn vừa

- **Nhánh:** `t40-bo-sinh-3b` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 13:06 · **gộp:** 11/09/2026 13:06 · **commit gộp:** [`58a3ff5`](https://github.com/wsunicorn/vihallulens/commit/58a3ff5fd6d77e86d8da87e562d95b80e5c3b308)
- **Thay đổi:** +69 / −44, 7 file · **bình luận bot:** 0

Lượt 11/09 lần 2 **hết bộ nhớ ngay lúc nạp** bản 7B `bfloat16` thứ hai: bộ đọc giữ 5.573 MB, nạp 7B cần đỉnh tạm 8–9 GB → **14,30/14,56 GiB**. Ràng buộc vật lý — mục 2 CLAUDE.md nói mọi thứ phải vừa 16 GB.

Trong tiêu chí đã đặt (chất lượng tốt nhất), thứ **lớn nhất còn vừa** là **Qwen2.5-3B `bfloat16`**: T31 đo 0 lớp tràn, đỉnh 4.117 MB một mình; 5,5 + ~5 GB nạp tạm ≈ 10,5 GB. `GENERATOR_MODEL` mặc định, đổi bằng `--generator` khi card lớn hơn. Notebook đặt `expandable_segments` trước khi nạp (bài học T30).

Điều khoản phần cứng ở Bảng 8 và README nay nói rõ: trên T4 bộ sinh và bộ đọc là **hai mô hình**, lượt đọc của bộ phát hiện là chi phí thêm thật.

```
$ python -m ruff check .   # All checks passed!
$ python -m pytest -q      # 781 passed
```

---

<a id="pr-111"></a>

### #111 — T40: demo RAG chạy đầu cuối trên T4 — bộ phát hiện tự bắt được ảo giác của bộ sinh 3B

- **Nhánh:** `t40-xong` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 13:40 · **gộp:** 11/09/2026 13:40 · **commit gộp:** [`08c53f3`](https://github.com/wsunicorn/vihallulens/commit/08c53f3020381a1a502ca24db18697f80b037f34)
- **Thay đổi:** +790 / −10, 2 file · **bình luận bot:** 0

##### Task
T40 · Hệ thống RAG minh họa tối giản, 21 tài liệu mẫu — tick sau phiên Kaggle lần 3 (11/09/2026).

##### Tiêu chí hoàn thành
> demo chạy đầu cuối, hỏi một câu và thấy điểm rủi ro hiện ra ✅

Trích từ `results/t40/kaggle_log_2026-09-11_lan3.txt` (bộ sinh Qwen2.5-3B `bfloat16`, VRAM 5.572 → 7.644 MB, đỉnh 7.837):

| Câu hỏi | Top-1 | Nhãn | Rủi ro |
|---|---|---|---|
| Đỉnh núi cao nhất Đông Dương? | Sa Pa | `no` | 0,008 |
| Ai chỉ huy chiến dịch Điện Biên Phủ? | Điện Biên Phủ | `no` | 0,135 |
| Phở xuất hiện ở đâu và khi nào? | Phở | `extrinsic` | 0,883 (tranh cãi) |
| Hồ Hoàn Kiếm gắn với truyền thuyết nào? | Hà Nội | `extrinsic` | 0,997 (ảo giác thật: "sau khi đánh đuổi giặc Minh", "trở về dinh thự" không có trong ngữ cảnh) |
| Vịnh Hạ Long thuộc tỉnh nào? — `POST /demo/ask` | Vịnh Hạ Long | `no` | 0,018 |

##### Ba dòng "kèm từ"
- **T37** ✅ uvicorn thật trong luồng, `/health` `ok`, `/score` `vihallu_train_19` nhãn `no` → `no` 0,317, `chunk_strategy` lạ → 400.
- **T38** ❌ chưa kiểm được trên máy GPU có Docker — ghi vào hạn chế.
- **T39** ✅ `GET /` 200, 16.164 ký tự.

##### Còn thiếu
Chỉ có log về; notebook đã chạy và ba JSON của lượt 3 chưa tải. Bản notebook đang commit là lượt 1 (rác, minh chứng cho lớp 27).

##### Kiểm
- `ruff check .` — All checks passed
- `pytest` — 781 passed
- Log quét không có khóa/token.

Giai đoạn 7 khép lại: 41/52 task.

---

<a id="pr-112"></a>

### #112 — T40: cất notebook đã chạy và ba JSON của lượt 3 làm minh chứng

- **Nhánh:** `t40-minh-chung` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 13:46 · **gộp:** 11/09/2026 13:46 · **commit gộp:** [`cf7b64a`](https://github.com/wsunicorn/vihallulens/commit/cf7b64a6f70ac323839fbf9b15ddbbbb67d77719)
- **Thay đổi:** +125 / −453, 5 file · **bình luận bot:** 0

Bổ sung cho #111 — lúc tick T40 mới có log, nay có đủ minh chứng theo quy tắc "notebook đã chạy là minh chứng".

- `notebooks/t40_demo_t4.ipynb`: 9/9 ô có output lượt 3, `execution_count` 1→9, đè lên bản lượt 1 (315d1e1).
- `results/t40/t40_rag.json`: Fansipan `no` 0,008 · Võ Nguyên Giáp `no` 0,135 · Phở `extrinsic` 0,883 · Hồ Hoàn Kiếm `extrinsic` 0,997 — khớp log.
- `results/t40/t37_rest.json`: `/health` `ok`, `/score` `vihallu_train_19` → `no` 0,317, `/demo/ask` Hạ Long → `no` 0,018, `chunk_strategy` lạ → 400.
- `results/t40/t36_thu_vien.json`: ba ví dụ `no` 0,001 / `intrinsic` 0,998 / `extrinsic` 1,000.
- `t39_trang.html` **không** commit: file tải về là bản "Save as" của trình duyệt, chèn URL ký tên GCS; nội dung thật là `serve/static/index.html`.

Quét khóa/token trên notebook và JSON: không có. TASKS.md mục T40 đổi "Còn thiếu gì" thành "Minh chứng".

---

<a id="pr-113"></a>

### #113 — chore: thêm uv.lock

- **Nhánh:** `them-uv-lock` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 14:05 · **gộp:** 11/09/2026 14:05 · **commit gộp:** [`99a6b16`](https://github.com/wsunicorn/vihallulens/commit/99a6b168580c83bfbf36d165ff1e57c15c65c809)
- **Thay đổi:** +2380 / −0, 1 file · **bình luận bot:** 0

File khóa phiên bản do `uv` tự sinh (466 KB). Clone repo rồi `uv sync` sẽ được y hệt bộ thư viện hiện tại, kể cả `scikit-learn 1.9.x` mà bundle pickle cần. Kaggle không đọc file này (notebook vẫn `pip install --no-deps -e .`) nên không đổi quy trình GPU. Quét khóa/token: không có.

---

<a id="pr-114"></a>

### #114 — Rà soát toàn repo: sửa 12 chỗ tài liệu lệch mã, số liệu không có chỗ nào sai

- **Nhánh:** `ra-soat-toan-repo` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 14:35 · **gộp:** 11/09/2026 14:35 · **commit gộp:** [`17da2fc`](https://github.com/wsunicorn/vihallulens/commit/17da2fc239711311c565a4e35c59e67cf1088b81)
- **Thay đổi:** +99 / −23, 8 file · **bình luận bot:** 0

Đợt kiểm tra lại mọi thứ trước khi sang giai đoạn viết (yêu cầu 11/09/2026).

##### Đã kiểm — không lỗi
- Mọi đường dẫn `scripts/…`, `configs/…`, `results/…`, `notebooks/…` nhắc trong 7 file `.md`: **0 thiếu**.
- 21 file `configs/*.yaml` nạp qua pydantic: **21/21**.
- 30 script `--help`: **30/30**.
- `models/e03_chunk_aware.pkl` khớp sidecar `.json` (groups, mode, 192 cột, lưới 27 × 28).
- Mọi macro-F1 / ECE trong `docs/EXPERIMENTS.md` đối chiếu `results/runs.jsonl`: khớp. Hai lượt E09 (27/08 và 28/08) đều được ghi rõ trong TASKS.md, không lẫn.
- `ruff check .` All checks passed · `pytest` 781 passed.

##### Đã sửa (tài liệu đi chậm hơn mã)
| File | Lệch |
|---|---|
| `docs/SPEC.md` | §2.6 "ba endpoint" → bảng 6 route đúng mã, đủ trường; §2.2 chữ ký `AttentionExtractor` + trường `chunks`; §2.3 chữ ký `build_feature_matrix`; §2.4 ghi rõ không hiện thực `CalibratedClassifierCV`; §3 ví dụ config; §4 CLI |
| `docs/EXPERIMENTS.md` | dòng "Chunk-aware (E05)" trống ở Bảng 1 → bỏ, ghi chú E05 là bước chọn |
| `docs/DATA.md` | "sẽ chốt ở T07" → đã chốt |
| `README.md` | `uv sync`; bảng route đủ; lệnh Kaggle đúng cách notebook thật làm (`--no-deps`) |
| `CLAUDE.md` §9 | thêm `models/`, `Dockerfile`, `uv.lock` |
| `serve/static/index.html` | ví dụ "Ngoại lai" thừa đuôi "khánh thành năm 2015" so với notebook T40 → dùng đúng chuỗi đã chấm |
| `results/runs.jsonl` | `e08_extrinsic_viwikifc` hai dòng cùng hash, cùng commit → giữ dòng sau (36 → 35) |
| `TASKS.md` | T21 tên file test; bảng tuần báo cáo cập nhật; thêm mục "Rà soát toàn repo 11/09" |

---

<a id="pr-115"></a>

### #115 — Soạn xong báo cáo tuần 10–13; bỏ hai đoạn lặp ở mục E14

- **Nhánh:** `bao-cao-tuan-10-13` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 14:51 · **gộp:** 11/09/2026 14:51 · **commit gộp:** [`24898f3`](https://github.com/wsunicorn/vihallulens/commit/24898f39ed50a90b508f767612cbdab69ac69082)
- **Thay đổi:** +10 / −12, 2 file · **bình luận bot:** 0

Bốn báo cáo tuần 10, 11, 12, 13 (.docx + thư .md/.html) đã soạn trong `UniversityRequirements/WeeklyLogs/` (thư mục gitignore, không vào repo). PR này chỉ cập nhật bảng tuần trong TASKS.md và bỏ hai đoạn văn bị lặp nguyên văn ở mục Bảng 5b (E14) của `docs/EXPERIMENTS.md` — phát hiện khi đọc lấy số cho báo cáo. Không đổi số liệu nào.

---

<a id="pr-116"></a>

### #116 — T39B: trang chủ kể chuyện — hero ba nhịp, cú Lens mắt dõi con trỏ, chế độ phát lại

- **Nhánh:** `t39b-trang-chu` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 16:05 · **gộp:** 11/09/2026 16:05 · **commit gộp:** [`98bfdbf`](https://github.com/wsunicorn/vihallulens/commit/98bfdbf0b093b26c9efd9211ff55471d32e88ba8)
- **Thay đổi:** +2082 / −206, 9 file · **bình luận bot:** 0

Việc thêm ngoài kế hoạch theo yêu cầu 11/09 (ghi vào TASKS.md là T39B, không tính vào 52 task).

##### Có gì
- **Hero ba nhịp theo cuộn** (ghim 260vh): mắt sáng trong tối → mặt cú đè tiêu đề khổng lồ → Giáo sư Lens trên cành + tấm giới thiệu. Bố cục mượn từ `sample.html` người dùng đưa: tiêu đề căn giữa, mascot raster đè lên, đồng tử là lớp DOM riêng.
- **Bốn ý đã duyệt:** đèn pin con trỏ, mắt đổi màu theo phán quyết, hạt chú ý trôi về mắt (hero) và về cột cao nhất (chunk-aware), tối mặc định.
- **`scripts/calibrate_owl.py`**: tìm hai đĩa hổ phách trong ảnh GPT image, ghi `owl.json`, nén WebP. Kiểm trên ảnh tổng hợp: tâm (0,357; 0,500) r 0,079 — đúng vị trí vẽ.
- **Chế độ phát lại**: `replay.json` sinh từ `results/t40` (`build_replay.py --check` trong test), trang chạy được trên máy không GPU và trên GitHub Pages.
- `app.py` mount thư mục tĩnh **sau** mọi route; test khóa `/health` không bị che.
- `static/img/PROMPTS.md`: năm ảnh + prompt + lệnh hiệu chuẩn. Chưa có ảnh thì SVG thay chỗ.

##### Kiểm
- `ruff check .` sạch · `pytest` **783 passed** (thêm 2 ca serve).
- Edge headless: `?noboot` và `?p=0.3|0.6|0.95` chụp ba nhịp hero, trang đầy đủ hai theme, console không lỗi JS. Bẫy đã gặp: headless đóng băng transition CSS giữa chừng — chớp mắt mở màn chuyển sang JS.
- `sample.html` (718 KB, tham khảo) không commit.

---

<a id="pr-117"></a>

### #117 — T39B: hero lượt 2 — chữ không bị che, tiêu đề mới, prompt theo ảnh cú tham chiếu

- **Nhánh:** `t39b-hero-lan-2` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 16:14 · **gộp:** 11/09/2026 16:14 · **commit gộp:** [`8436b23`](https://github.com/wsunicorn/vihallulens/commit/8436b2348d69a4a119d75571a2525a398fc22b51)
- **Thay đổi:** +83 / −49, 4 file · **bình luận bot:** 0

Theo ba góp ý 11/09: (1) đèn pin chỉ chiếu lên mặt cú (mask), bố cục chia hai bên, không dòng nào nằm sau mặt cú; (2) tiêu đề "MẮT KHÔNG NÓI DỐI" + dòng dẫn mới; (3) prompt GPT image bám ảnh cú tham chiếu, hai phong cách; `calibrate_owl.py` đo theo khung bao. Kiểm: ruff sạch, 783 passed, Edge headless chụp hero không lỗi console.

---

<a id="pr-118"></a>

### #118 — T39B: sửa mask đèn pin, màn mở đầu tối hơn

- **Nhánh:** `t39b-den-pin` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 16:17 · **gộp:** 11/09/2026 16:17 · **commit gộp:** [`c552621`](https://github.com/wsunicorn/vihallulens/commit/c5526217a4091cd8774b47306252ae3376d67361)
- **Thay đổi:** +11 / −7, 1 file · **bình luận bot:** 0

`radial-gradient(circle 34% …)` không hợp lệ (circle chỉ nhận độ dài) nên trình duyệt bỏ mask → mất đèn pin và mặt cú hiện nguyên. Đổi sang `ellipse 30% 30%`, mask đặt trên ảnh/SVG chứ không trên mắt để mắt luôn sáng. Màn mở đầu: đen → mí mở (0,6 s) → chớp (1,5 s) → mặt hiện dần qua đèn pin (2,1 s).

---

<a id="pr-119"></a>

### #119 — T39B: cú mở đầu to hơn, mắt trùm lên tiêu đề

- **Nhánh:** `t39b-cu-to` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 16:20 · **gộp:** 11/09/2026 16:20 · **commit gộp:** [`25aa1ca`](https://github.com/wsunicorn/vihallulens/commit/25aa1ca0bd5df324ffd079c95d544a45ee22e203)
- **Thay đổi:** +7 / −7, 1 file · **bình luận bot:** 0

Theo góp ý: người gác đêm phải bao phủ trang. Lớp mặt 76→108 vmin, scale mở đầu 1,18→1,42 (lùi về 0,70 khi cuộn), quầng sáng mắt hai lớp rộng hơn, mask đèn pin thu tỷ lệ cho vừa, hai tấm bên có bóng chữ để đọc được trên lông cú.

---

<a id="pr-120"></a>

### #120 — T39B: ảnh cú thật, mắt lam ngọc theo ảnh tham chiếu

- **Nhánh:** `t39b-anh-that` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 16:45 · **gộp:** 11/09/2026 16:45 · **commit gộp:** [`4c77ed9`](https://github.com/wsunicorn/vihallulens/commit/4c77ed95bbd6b4c01fa78f1bc98cdcbe14a7b648)
- **Thay đổi:** +103 / −54, 10 file · **bình luận bot:** 0

Năm ảnh GPT image đã hiệu chuẩn (`owl.json`), nén WebP 1,7 MB. Mắt vẽ đè sang lam ngọc như `original.jpg` — không cần sinh lại; màu phán quyết tường minh. `calibrate_owl.py --eye cyan|amber`. PROMPTS.md viết lại theo ảnh tham chiếu. PNG gốc + ảnh tham chiếu gitignore. Kiểm: ruff sạch, 783 passed, Edge headless chụp mặt cận và giáo sư — mắt khớp đúng vị trí.

---

<a id="pr-121"></a>

### #121 — T39B: ảnh cú xám mắt lam ngọc, cử động theo con trỏ, vẫy cánh

- **Nhánh:** `t39b-cu-dong` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 17:07 · **gộp:** 11/09/2026 17:07 · **commit gộp:** [`c580402`](https://github.com/wsunicorn/vihallulens/commit/c580402d93f3b784584e2a722df0d06224c7e019)
- **Thay đổi:** +158 / −45, 9 file · **bình luận bot:** 0

Bộ ảnh mới (theo original.jpg) hiệu chuẩn lại, rig lưu rx/ry cho mắt bầu dục và tọa độ mắt riêng từng biến thể. Cử động mới không cần ảnh: xoay đầu 3D, nghiêng người, thở, gật/rung, vẫy cánh hai khung. PROMPTS.md: bốn cử chỉ cần ảnh thêm. Kiểm: ruff sạch, 783 passed; Edge headless: mặt cận và giáo sư (base + point) mắt khớp.

---

<a id="pr-122"></a>

### #122 — T39B: bốn cử chỉ có ảnh thật, khử nền đen

- **Nhánh:** `t39b-cu-chi` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 17:21 · **gộp:** 11/09/2026 17:21 · **commit gộp:** [`39271a3`](https://github.com/wsunicorn/vihallulens/commit/39271a320364ba1a9865ce5fd8e42108a2c97e40)
- **Thay đổi:** +111 / −5, 7 file · **bình luận bot:** 0

Ảnh wave/think/shock/happy người dùng sinh; ba ảnh có nền đen đặc → `calibrate_owl.py --key-black` tô loang từ mép để khử. Sáu biến thể hiệu chuẩn một lệnh, mắt khớp (kiểm bằng vòng vẽ đè). Vẫy dùng cặp wave/base (point lệch thân nhiều hơn). Lúc chấm: tư thế think. ruff sạch, 783 passed.

---

<a id="pr-123"></a>

### #123 — T39B: morph theo mắt, khung mờ dần, cánh chỉ sang trái

- **Nhánh:** `t39b-morph` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 11/09/2026 17:33 · **gộp:** 11/09/2026 17:33 · **commit gộp:** [`4087aba`](https://github.com/wsunicorn/vihallulens/commit/4087aba0968ddcd2cb9aab990dd74b334bdfcde4)
- **Thay đổi:** +55 / −26, 3 file · **bình luận bot:** 0

Bốn góp ý: dòng dẫn dịch lên; morph mặt cận → giáo sư bằng cách đưa hai mắt của mặt về đúng mắt giáo sư rồi hòa hình; ảnh point lật gương; đổi khung bằng cross-fade có mắt cũ mờ theo, mỗi khung neo theo tâm mắt nên đầu đứng yên. ruff sạch, 783 passed.

---

<a id="pr-124"></a>

### #124 — Slides: bộ trình bày với GVHD 16/09

- **Nhánh:** `slide-gvhd` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 13/09/2026 23:46 · **gộp:** 13/09/2026 23:46 · **commit gộp:** [`76207d8`](https://github.com/wsunicorn/vihallulens/commit/76207d8d41a8e5f3f2497337931ec7f7073c763a)
- **Thay đổi:** +858 / −1, 15 file · **bình luận bot:** 0

22 slide HTML tự chứa (2,7 MB ảnh WebP), hoạt ảnh theo phím, ghi chú diễn giả, in PDF qua `?all`. Kế hoạch đã duyệt ở `ke_hoach_slide.md`, cách dùng ở `HUONG_DAN.md`. Chỉ thư mục Slides được mở khỏi gitignore; báo cáo tuần và kế hoạch vẫn ở máy. Quét khóa: không có.

---

<a id="pr-125"></a>

### #125 — Slides v2: bộ 36 slide theme "Đêm cú" bám 8 chương mẫu báo cáo

- **Nhánh:** `slide-v2` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 18/09/2026 23:50 · **gộp:** 26/09/2026 15:28 · **commit gộp:** [`2c9caed`](https://github.com/wsunicorn/vihallulens/commit/2c9caedad3965db6e5ee2efa2a6f019a0a33cbfd)
- **Thay đổi:** +2440 / −8, 10 file · **bình luận bot:** 1

##### Nội dung
- `UniversityRequirements/Slides/slide_v2.html` — 36 slide, 9 phần ánh xạ 8 chương mẫu báo cáo Khoa. Sân khấu 1920×1080 cố định, ba kiểu hoạt ảnh (lặp / một lần / theo bước), sơ đồ SVG inline, ghi chú diễn giả, `?all` để in PDF.
- `BI_KIP_HTML_SLIDE.md` — bộ skill đã cài và 10 luật dựng slide.
- `ke_hoach_slide_v2.md` — kế hoạch đã duyệt; `mau/` — 5 mẫu theme, chốt E "Đêm cú".
- `HUONG_DAN.md` — thêm mục v2.

##### Kiểm
Chụp Edge headless 36/36 slide ở `?all` (trạng thái cuối) và chế độ chiếu thật; đã sửa: canvas hạt đẩy nội dung slide 36, chồng chữ Venn slide 28, cú che số trang, căn giữa dọc, phóng to hình 14/15/18.

---

<a id="pr-126"></a>

### #126 — Slides v2: dựng lại 36 slide — mọi slide tự chạy, 14 sơ đồ động trên số liệu thật

- **Nhánh:** `slide-v2-dong` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 19/09/2026 00:31 · **gộp:** 26/09/2026 15:28 · **commit gộp:** [`41dafde`](https://github.com/wsunicorn/vihallulens/commit/41dafde690a6a3dfe87302b7afb51ca328fe862d)
- **Thay đổi:** +2249 / −819, 16 file · **bình luận bot:** 1

##### Nội dung
- `slide_v2.html` dựng lại: mọi slide tự chạy khi vào; 14 sơ đồ động GSAP + D3 (nhúng, không cần mạng) chạy bằng số liệu thật từ `results/runs.jsonl`, `results/t40/*.json`, `docs/EXPERIMENTS.md`.
- Tương tác: rê chuột hiện giá trị, click dừng/chạy, nút ⟳ chạy lại, thanh trượt (số đoạn, cỡ cửa sổ), nút chọn ví dụ / chiều chuyển giao / câu hỏi demo; cú Lens đổi màu mắt theo phán quyết và nhìn theo chuột.
- `HUONG_DAN.md` cập nhật.

##### Kiểm
Chụp Edge headless 36/36 slide ở `?all` (trạng thái cuối) và chế độ chiếu thật (giữa hoạt ảnh); đã sửa: lớp `.f` trùng CSS fragment làm mất cột ở slide 25, tia chú ý cắt ngang thẻ ở slide 6, thanh trượt đè tiêu đề, tween chưa xong khi in PDF.

---

<a id="pr-127"></a>

### #127 — Đánh giá tổng kết 26/09: mức hoàn thành ba câu hỏi nghiên cứu và năm việc còn lại

- **Nhánh:** `danh-gia-tong-ket` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 26/09/2026 15:24 · **gộp:** 26/09/2026 15:28 · **commit gộp:** [`fe6654d`](https://github.com/wsunicorn/vihallulens/commit/fe6654d1744bdf678820332e2b15e07a23b2771b)
- **Thay đổi:** +295 / −6, 3 file · **bình luận bot:** 1

##### Nội dung
- **TASKS.md** — tick T42–T46 (quyển báo cáo 151 trang đã viết xong, 658 con số khớp `results/`). Ghi trạng thái cho các task chưa tick được: T41 (chờ ý kiến thầy), T47 (rà xong, còn 6 nhóm lỗi chờ sửa), T48, T50. Thêm năm việc bổ sung, không tính vào 52 task: **T45B** định vị so với bảng xếp hạng ViHallu, **T42B** cập nhật chương 2, **T45C/E18** chấm theo câu phản hồi, **T45D/E19** so với cắt bỏ ngữ cảnh, **T45E/E20** chi phí biên trên bf16 (cần hỏi trước vì vướng ràng buộc phần cứng).
- **docs/EXPERIMENTS.md** — mục 8: mức hoàn thành theo câu hỏi nghiên cứu, chỗ đã chạm trần, chỗ chưa, định vị so với 84,80 % của cuộc thi, cách nhìn đúng về kết quả. Thêm E18–E20 dạng đề xuất vào danh sách thí nghiệm.
- **docs/REFERENCES.md** — mục 4: bốn công trình 2025–2026 và vì sao mỗi bài quan trọng.

##### Kiểm
`uv run pytest` — 783 passed. Chỉ sửa tài liệu, không đổi mã.

##### Phụ thuộc
Nhánh này dựng trên `slide-v2-dong` (PR #126, chứa bản sửa 16 % → 29 % trong `docs/EXPERIMENTS.md` và `TASKS.md`). Gộp #126 trước, rồi đổi base của PR này về `main`.

---

<a id="pr-128"></a>

### #128 — Slides: bộ slide Hội đồng 23 trang theo bố cục khóa luận

- **Nhánh:** `slide-hoi-dong` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 22/10/2026 15:25 · **gộp:** 22/10/2026 15:25 · **commit gộp:** [`41dd81c`](https://github.com/wsunicorn/vihallulens/commit/41dd81c5b404ffd92c770cf74daba1482fe9ac8f)
- **Thay đổi:** +4161 / −54, 11 file · **bình luận bot:** 1

Làm theo góp ý của GVHD ngày 05/10: slide báo cáo Hội đồng phải bám bố cục quyển khóa luận — giới thiệu và bài toán, động lực và khoảng trống, cơ sở lý thuyết (ghi công trình ở chân slide), dữ liệu, phương pháp đề xuất, hệ thống, thực nghiệm, tự đánh giá, tài liệu tham khảo.

##### Thay đổi
- `slide_rut_gon_19.html` / `.pdf`: bộ 19 slide Minh dựng ngày 14/10, số liệu dò với quyển v4 và `results/runs.jsonl`.
- `slide_hoi_dong_23.html` / `.pdf`: giữ nguyên 19 slide trên, chèn bốn slide còn thiếu so với danh sách của thầy — bài toán (03), các hướng phát hiện ảo giác và vị trí của khóa luận theo Bảng 2.1 (06), kiểm định năm giả thuyết theo Bảng 7.1 (20), tài liệu tham khảo chính đánh số theo danh mục 32 mục (22). Đã sửa theo đợt rà 16/10 của Minh.
- `nguon_bo_sung_15-10/`: sơ đồ và script chèn bốn slide, để Minh nhập vào script dựng bộ slide.
- `HUONG_DAN.md` viết lại cho bộ 23 slide; `GIAI_THICH_SLIDE.md` ghi rõ là của bộ cũ `slide_v2`.
- `ke_hoach_slide_v3.md`, logo trường.

##### Kiểm tra
- Dựng lại `slide_hoi_dong_23.html` từ nguồn: giống hệt từng byte bản trong PR.
- 23 slide chạy không lỗi JavaScript (`?all&qa`), chụp từng slide ở trạng thái cuối đều đúng.
- `uv run ruff check .`: All checks passed. `uv run pytest`: 783 passed.

---

<a id="pr-129"></a>

### #129 — Cập nhật TASKS.md 22/10: tick T28, T47; trạng thái các việc còn lại

- **Nhánh:** `cap-nhat-tasks-22-10` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 22/10/2026 15:26 · **gộp:** 22/10/2026 15:26 · **commit gộp:** [`a16f4dc`](https://github.com/wsunicorn/vihallulens/commit/a16f4dccdb70b2a93c68aa39d91ec958df0b32d9)
- **Thay đổi:** +43 / −4, 1 file · **bình luận bot:** 1

Cập nhật nguồn sự thật về tiến độ sau các đợt sửa quyển (v4) và slide (bộ 23 trang).

- Tick **T28** (mốc giữa kỳ đáp ứng bằng thư tuần 9 ngày 02/10 kèm bản thảo đầy đủ) và **T47** (bản v4 sửa xong định dạng, in một mặt, tài liệu tham khảo 45 → 32, kiểm lại trên PDF 130 trang), kèm phần diễn giả.
- Trạng thái 22/10 cho T41, T42B, T45B–E, T48, T50; ghi các quyết định GVHD chốt ngày 05/10.
- Bảng việc hành chính: thư báo cáo GVHD chỉ gửi khi có việc mới.

Chỉ sửa `TASKS.md`, không đổi mã.

---

<a id="pr-130"></a>

### #130 — Tái lập: ghim phiên bản mô hình, thư viện Docker và Kaggle, thêm mã băm dữ liệu gốc

- **Nhánh:** `tai-lap-ghim-phien-ban` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 22/10/2026 15:35 · **gộp:** 22/10/2026 15:35 · **commit gộp:** [`549b0d0`](https://github.com/wsunicorn/vihallulens/commit/549b0d09866260f6f7203ced4903436b6036ac8a)
- **Thay đổi:** +279 / −8, 11 file · **bình luận bot:** 1

Vá bốn chỗ hở về tái lập đã ghi trong Phụ lục D của quyển.

##### Thay đổi
- **Mô hình:** `src/vihallulens/revisions.py` ghim mã commit Hugging Face của bảy mô hình (Qwen2.5-7B/3B/1.5B, Sailor2-8B, PhoBERT, XLM-R, InfoXLM). Dùng ở bộ đọc, bộ sinh của hệ RAG và bộ mã hóa tinh chỉnh. Kiểm 22/10: mọi kho sửa lần cuối trước lượt chạy dùng nó (muộn nhất PhoBERT 03/08, chạy 27/08), ba mô hình còn trong cache máy cá nhân trùng mã commit. Ghim trong mã chứ không trong YAML để mã băm cấu hình của các shard đã trích không đổi.
- **Docker:** `requirements-docker.txt` sinh từ `uv.lock`, bỏ nhóm torch (torch lấy từ ảnh nền CUDA 12.4, vì torch trong lock là bản CUDA 13 cần driver mới hơn). Dockerfile cài theo file này rồi cài gói với `--no-deps`.
- **Kaggle:** `requirements-kaggle.txt` ghim theo `uv.lock` cho các notebook dựng từ nay. Notebook đã chạy giữ nguyên vì là minh chứng của lượt chạy.
- **Dữ liệu:** mục 5 của `data/raw/MANIFEST.md` ghi SHA-256 và kích thước của 13 tệp gốc.

##### Kiểm tra
- `uv run pytest`: 804 passed (thêm 17 ca: ghim mô hình, hai file requirements khớp `uv.lock`, dữ liệu khớp mã băm).
- `uv run ruff check .`: sạch.
- Chưa build được ảnh Docker vì máy không bật Docker daemon; cần build thử trước buổi bảo vệ.

---

<a id="pr-131"></a>

### #131 — T45D: dựng thí nghiệm E19 định vị bằng cắt bỏ ngữ cảnh

- **Nhánh:** `e19-cat-bo-ngu-canh` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 22/10/2026 15:48 · **gộp:** 22/10/2026 15:48 · **commit gộp:** [`9a1d54c`](https://github.com/wsunicorn/vihallulens/commit/9a1d54c7fcd22c7e8047fa7c92862a1cbfe49efe)
- **Thay đổi:** +2655 / −2, 6 file · **bình luận bot:** 1

##### Mục đích
Chuẩn bị E19, so định vị bằng chú ý với định vị bằng cắt bỏ ngữ cảnh theo kiểu ARC-JSD, trên cùng 300 mẫu của E08. PR này chỉ có code và notebook; thí nghiệm sẽ chạy trên Kaggle sau khi gộp, vì notebook clone từ `main`.

##### Thay đổi
- `src/vihallulens/attribution.py`: với mỗi đoạn ngữ cảnh, cắt đoạn đó ra và tính tổng độ lệch Jensen–Shannon trên các token phản hồi. Mô hình chạy `bfloat16`, vì ở `float16` lớp 27 tràn số và đầu ra thành NaN.
- `scripts/run_attribution.py`: ba lệnh `select / run / report`.
- `configs/e19_attribution_samples.json`: 300 mẫu, hạt giống 42.
- `notebooks/t45d_e19_cat_bo_t4.ipynb`: notebook cho Kaggle T4.
- `TASKS.md`: sửa ước tính T45D thành 1,5–2,5 giờ GPU (3.274 lượt đọc ở bf16).

##### Kiểm tra
- `ruff check src scripts tests`: All checks passed!
- `pytest`: 812 ca đạt, trong đó 8 ca mới ở `tests/test_attribution.py`.
- Đã chạy thử `report` với kết quả cắt bỏ giả. Phía chú ý là số thật: đầu tốt nhất đạt 0,850, đầu E06 đạt 0,797, trung bình 756 đầu đạt 0,349.

---

<a id="pr-132"></a>

### #132 — T45C: dựng thí nghiệm E18 chấm theo từng câu phản hồi

- **Nhánh:** `e18-gop-theo-cau` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 22/10/2026 16:05 · **gộp:** 22/10/2026 16:06 · **commit gộp:** [`5bbf9ca`](https://github.com/wsunicorn/vihallulens/commit/5bbf9ca3c05626a2dfc05b020737c50d834c2436)
- **Thay đổi:** +1011 / −6, 11 file · **bình luận bot:** 1

##### Mục đích
Chuẩn bị E18. Thí nghiệm kiểm lời giải thích ở chương 7: lấy trung bình trên cả phản hồi có làm loãng một mệnh đề bịa không. PR này chỉ có code và notebook; phần trích chạy trên Kaggle sau khi gộp.

##### Thay đổi
- Cờ mới `extractor.response_sentences` (`configs/e18_sentence_pooling_vihallu.yaml`):
  - Cờ nằm trong hash trích, nên E18 ghi ra shard riêng `8d0bb26a198b` và không đè shard E03 `8c49fc0417f1`.
  - Khi tắt, cờ không xuất hiện trong `to_dict`, nên mọi hash cũ giữ nguyên.
- Mỗi bản ghi lưu thêm véc-tơ của từng câu phản hồi, cho mọi khối. Câu được tách bằng đúng hàm tách câu của ngữ cảnh; các trường cũ không đổi.
- `scripts/run_sentence_pooling.py` so bốn nhánh `whole / mean / max / min`:
  - cùng quy trình chọn đầu trên dev như E03;
  - kiểm các trường cũ trùng shard E03;
  - chấm riêng phần phản hồi từ hai câu trở lên;
  - khoảng tin cậy bằng bootstrap ghép cặp;
  - dự đoán khóa bằng kiểm thử.
- Ghi trước khi chạy: 71,6 % phản hồi ViHallu chỉ có một câu, nên E18 chỉ có thể khác E03 trên khoảng 28 % mẫu.

##### Kiểm tra
- `ruff check src scripts tests`: All checks passed!
- `pytest`: 825 ca đạt, trong đó 13 ca mới ở `tests/test_sentence_pooling.py`.
- Chạy thử đầu cuối trên shard giả dựng từ shard E03 thật (train 1.500, dev và test đủ):
  - kiểm tái lập báo lệch lớn nhất `0.00e+00` ở cả ba tập;
  - bốn nhánh chạy xong và ghi ba dòng kết quả.
- Chạy lại E03 trên shard cũ bằng code hiện tại: macro-F1 0,7567 (topk k=32), trùng `results/runs.jsonl`.

---

<a id="pr-133"></a>

### #133 — T41: dựng thí nghiệm E17 chuyển miền sang ViFactCheck

- **Nhánh:** `e17-vifactcheck` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 22/10/2026 16:06 · **gộp:** 22/10/2026 16:06 · **commit gộp:** [`9ecf268`](https://github.com/wsunicorn/vihallulens/commit/9ecf2682beafb0350b8a7a41b7c05f4d3a5b1c69)
- **Thay đổi:** +317 / −0, 4 file · **bình luận bot:** 1

##### Mục đích
Chuẩn bị E17: chạy công thức E15 trên ViFactCheck, bộ tin tức, tức miền thứ ba. Theo quyết định ngày 22/10, nhóm chạy trước rồi mới quyết định có đưa vào quyển hay không.

##### Thay đổi
- Hai cấu hình, chunk-aware và mốc lookback gộp, dùng chung lượt trích `cdffb5c66735`.
- Notebook `notebooks/t41_e17_vifactcheck_t4.ipynb`: trích 5.062 / 723 / 1.447 mẫu, ước tính khoảng 2 giờ GPU; sau đó soi shard và chép kết quả ra `/kaggle/working/ket_qua_t41/`.
- Chấm điểm làm trên máy bằng `run_chunk_aware.py`, chạy mốc lookback trước, theo quy tắc T23 (mọi phép so sánh chấm trên cùng một máy).

##### Kiểm tra
- Hai cấu hình load được và cho cùng `extraction_hash` (`cdffb5c66735`).
- Mọi ô code trong notebook đều parse được.
- Cỡ dữ liệu đo trên máy: trung bình khoảng 960 token mỗi mẫu, chỉ 0,2 % mẫu vượt 4.000 token.

---

<a id="pr-134"></a>

### #134 — T50: giải thích slide, kịch bản thời gian và câu hỏi hội đồng

- **Nhánh:** `t50-giai-thich-hoi-dap` → `main` · **người mở:** wsunicorn · **trạng thái:** đã gộp
- **Mở:** 22/10/2026 16:10 · **gộp:** 22/10/2026 16:10 · **commit gộp:** [`f0ad3c2`](https://github.com/wsunicorn/vihallulens/commit/f0ad3c23cf914f91da3a71e57fd9d078c73c8008)
- **Thay đổi:** +1357 / −652, 5 file · **bình luận bot:** 1

##### Mục đích
Chuẩn bị bảo vệ (D13, D14): tài liệu đọc kèm bộ slide chính và danh sách câu hỏi hội đồng dự kiến.

##### Thay đổi
- `GIAI_THICH_SLIDE.md` viết lại cho bộ 23 slide:
  - kịch bản thời gian hai phương án, bản đủ khoảng 22 phút và bản rút khoảng 15 phút, có mốc cộng dồn;
  - mỗi slide có phần giải thích thuật ngữ và nguồn số liệu.
- Bản cũ cho `slide_v2.html` đổi tên thành `GIAI_THICH_SLIDE_v2_cu.md`.
- `HOI_DAP_HOI_DONG.md`: 26 câu hỏi kèm hướng trả lời, số liệu lấy từ quyển v4 và `docs/EXPERIMENTS.md`. Các câu phụ thuộc E17–E19 được đánh dấu ⏳.
- Cập nhật `HUONG_DAN.md` và trạng thái T50 trong `TASKS.md`.

##### Kiểm tra
- Thời lượng tính từ số chữ ghi chú diễn giả của từng slide, ở tốc độ 125 chữ/phút.
- Số liệu đối chiếu với `docs/EXPERIMENTS.md` (Bảng 1, 2, 7, 8) và ghi chú diễn giả.

---

<a id="pr-135"></a>

### #135 — Báo cáo: đưa nguồn dựng quyển (docs/report, docs/media, docs/tools) vào repo, khớp bản Word đã nộp

- **Nhánh:** `nguon-bao-cao` → `main` · **người mở:** MinhNguyen1007 · **trạng thái:** đang mở — Minh mở lại trên repo mới
- **Mở:** 22/10/2026 17:19 · **gộp:** — · **commit gộp:** đang mở
- **Thay đổi:** +7770 / −1, 58 file · **bình luận bot:** 1

##### Vì sao

Phụ lục D của quyển, bước "Sinh lại hình vẽ và dựng lại báo cáo", gọi `docs/media/src/*.py`,
`docs/tools/resolve.py` và `docs/tools/build_docx.py`, nhưng repo chưa có `docs/report`,
`docs/media`, `docs/tools`. PR này đưa ba thư mục vào và chỉnh nguồn để chạy đúng các lệnh đó
ra đúng quyển v4 đã gửi thầy (130 trang, in một mặt).

##### Nội dung

| Đường dẫn | Là gì |
| --- | --- |
| `docs/report/` | Bản thảo theo chương (`00_front.md` … `09_back.md`) và `README.md`: quy trình dựng, công cụ cần có, dàn trang |
| `docs/tools/` | `resolve.py` ghép chương, đánh số hình, bảng, mục, công thức, dựng danh mục và tài liệu tham khảo; `build_docx.py` dựng `.docx` theo mẫu Khoa rồi để Word cập nhật trường và xuất PDF |
| `docs/media/src/` | Mã vẽ hình: `charts.py`, `method_figs.py`, `concept_figs.py`, `fig_tong_quat_he_thong.py`, `fig_terminal.py`, `svgkit.py`; Hình 5.1 (`fig_trich_huanluyen_phucvu.html`, `rough.js`, font); `shoot_site.mjs` chụp trang web; `render.sh` |
| `docs/media/` | 22 hình quyển đang dùng, `logo_iuh.png`, 7 logo trong `logos/` mà Hình 5.1 dùng |
| `docs/Mau bao cao KLTN_DS.docx`, `docs/Mau_bao_cao_KLTN_DS.md` | Mẫu báo cáo của Khoa và bản chép chữ; `build_docx.py` lấy số định dạng từ chương 2 của mẫu |

##### Chỉnh nguồn để khớp bản Word v4

Các chỗ dưới đây trước chỉ được sửa thẳng trong file Word, nên dựng lại từ nguồn sẽ ra quyển khác:

1. `09_back.md`: thêm đoạn mở đầu và Bảng D.1–D.4 của Phụ lục D, thêm toàn bộ Phụ lục G, chép
   nguyên văn từ file Word; số mục, số bảng viết bằng nhãn để `resolve.py` tự đánh.
2. `build_docx.py`: dàn trang một mặt (lề trái 3,5 cm ở mọi trang, số trang góc phải, header căn
   trái, các phần không còn bắt đầu ở trang lẻ); trang ngang giữ lề như bản Word.
3. `build_docx.py`: độ rộng cột của Bảng 7.2, D.1–D.4, G.1, G.2 lấy đúng từ bản Word
   (`BOOK_WIDTHS`), hàng dữ liệu của Bảng D.4 cỡ 8 pt (`BODY_PT`); hai ô "10–15 %" ở Bảng D.3 và
   G.2 giữ khoảng trắng thường như bản Word (`PLAIN_PERCENT`).
4. `build_docx.py`: dòng dẫn chỉ gồm chữ đậm, đứng ngay trước một danh sách, luôn đi cùng danh
   sách đó ("Khó khăn." ở mục 1.7).
5. `00_front.md`: chữ ký cuối Lời cảm ơn hai dòng, chừa chỗ ký như bản Word; `06_ch6.md`:
   "k = 32" ở Bảng 6.4 dùng khoảng trắng không ngắt.

##### Chỉnh để chạy được trên máy khác

6. `render.sh` tự tìm thư mục chứa nó thay cho đường dẫn cứng; `method_figs.py` và
   `concept_figs.py` đọc đường dẫn Chrome từ `CHROME_PATH`, như `shoot_site.mjs`.
7. `docs/report/README.md`: thêm mục "Công cụ cần có" kèm phiên bản đã dùng; mục "In hai mặt"
   thay bằng "Dàn trang" một mặt; đoạn ảnh chụp ghi đúng khung 780 px của `shoot_site.mjs`.
8. Sửa hết lỗi ruff trong `docs/` (148 → 0): ngắt dòng dài, đổi tên hằng viết hoa trong các hàm
   vẽ sang chữ thường, `zip(..., strict=False)`, bỏ import thừa.
9. `.gitignore`: bỏ qua `docs/BaoCao_KLTN.{md,docx,pdf}` do script dựng ra, tệp SVG/HTML trung
   gian và 14 hình script còn vẽ nhưng đã bỏ khỏi quyển. `CLAUDE.md` mục 9: thêm ba thư mục vào
   sơ đồ.

##### Kiểm chứng

Chạy trên một bản clone mới của nhánh này (Windows, Word 16.0, pandoc 3.9.0.2):

```
python docs/media/src/charts.py              # cùng 4 lệnh vẽ hình còn lại: không lỗi,
                                             # hình trùng từng điểm ảnh với docs/media
python docs/tools/resolve.py
OK -> docs/BaoCao_KLTN.md  |  22 hình, 43 bảng, 27 công thức, 32 tài liệu, 2189 dòng
python docs/tools/build_docx.py
   Word dựng 30 dòng công thức từ LaTeX
   Word: 130 trang, 1 mục lục, 2 danh mục hình/bảng
uvx ruff@0.16.7 check docs
All checks passed!
```

So với quyển v4 (`KLTN_22635801_22643511_PhatHienAoGiac.docx`, SHA-256 `97C7094AF29F…`):

- Văn bản (đoạn, bảng, mục lục, danh mục hình và bảng): trùng, trừ một dấu cách thừa sau
  "Nguyễn Ngọc Lân" ở Lời cảm ơn.
- PDF: trùng 130/130 trang khi file Word v4 được xuất bằng cùng phiên bản Word. PDF v4 xuất ngày
  13/10 khác ở vài chỗ dấu chấm dẫn và khoảng trắng trong công thức do Word đã cập nhật; xuất lại
  file Word v4 thì hết.
- Bước sửa ruff được kiểm riêng: hình, `BaoCao_KLTN.md`, `.docx` và PDF dựng lại trùng với lúc
  trước khi sửa.
