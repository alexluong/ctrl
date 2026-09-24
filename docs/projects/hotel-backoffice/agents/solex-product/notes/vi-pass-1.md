# Vietnamese pass 1 — solex c8b3528 (2026-09-25)

65 en-only keys from `pnpm i18n:report` + one QA fix. Sent to solex-dev; dev applies to `src/i18n/messages.ts` `vi` and commits. Terms follow existing vi (đặt phòng · lượt lưu trú · hoá đơn · khoản mục · bảng giá · "Đã …" for events) and ezFolio desk words (Nguồn, Khách lẻ/Đoàn, Ghi chú).

## Fix (QA)
`folio.void`: "Huỷ" → "Huỷ khoản" (ask dialog had Void and Cancel both "Huỷ"; `ask.cancel` stays "Huỷ").

## Pairs
```
setup.bookingSources = Nguồn đặt phòng
setup.bookingSourcesHint = Đặt phòng đến từ đâu — mục Nguồn của ezFolio. Là danh sách chứ không cố định trong mã, nên thêm một OTA chỉ là thêm một dòng, không cần phát hành bản mới. Nhóm là thứ báo cáo doanh thu dùng để đếm.
setup.noBookingSources = Chưa có. Khi chưa có nguồn nào, mọi đặt phòng được ghi là khách vãng lai.
setup.sourceKind = Tính là
setup.addBookingSource = Thêm nguồn
setup.seedBookingSources = Thêm danh sách chuẩn
sourceKind.direct = Trực tiếp
sourceKind.ota = OTA
sourceKind.agent = Đại lý du lịch
sourceKind.company = Công ty
error.setup.sourceKindInvalid = Chọn kênh này tính là gì.
error.setup.roomTypeInvalid = Loại phòng này khách sạn không còn dùng nữa.
booking.source = Nguồn
booking.addLine = Thêm loại phòng khác
booking.removeLine = Bỏ dòng này
booking.freeOfType = Trống {free}
booking.freeShort = Trống {free}, cần {asked}
booking.supplyHint = Số phòng còn lại của từng loại, theo từng đêm. Đêm đã giữ đều được tính, dù đã xếp phòng hay chưa — và không có gì từ chối một đoàn vì thiếu phòng, nên đây là chỗ duy nhất cho thấy điều đó.
booking.cancel = Huỷ đặt phòng
booking.cancelReason = Lý do huỷ?
booking.cancelHint = Mọi phòng còn giữ theo đặt phòng này cũng bị huỷ, và các đêm được mở bán lại.
booking.partyTitle = Đặt phòng đứng tên ai
booking.partyHint = Người liên hệ là người đã đặt. Sửa tên hay số điện thoại là sửa người đó, không phải sửa đặt phòng này.
booking.partyContact = Người đặt
booking.savedParty = Lưu người đứng tên
booking.notesTitle = Ghi chú về đặt phòng
booking.notesHint = Điều lễ tân cần nhớ về đặt phòng này.
booking.saveNotes = Lưu ghi chú
booking.roomsTitle = Phòng trong đoàn này
booking.roomsHint = Phòng thêm ở đây chưa có số phòng — xếp phòng ở trang riêng của nó, nơi lịch phòng cho biết phòng có trống hay không.
booking.addRoom = Thêm phòng
booking.removeTitle = Bớt phòng
booking.removeHint = Các đêm được mở bán lại. Phòng đã có khách vào ở thì không bớt được.
booking.removeRooms = Bớt
booking.removeNone = Chọn ít nhất một phòng.
error.booking.notEditable = Đặt phòng này đã kết thúc, không sửa được nữa.
error.booking.nothingToChange = Không có gì thay đổi.
error.booking.stayCheckedIn = Đã có khách nhận phòng theo đặt phòng này. Hãy trả phòng cho họ, hoặc huỷ những phòng chưa đến.
stay.nightAction = Sửa
stay.nightOnBill = đã lên hoá đơn
stay.saveRate = Lưu
stay.removeNight = Trả lại đêm
stay.addNight = Thêm một đêm
stay.addNightRate = Giá
stay.addNightAction = Thêm
stay.addNightHint = Đêm ngay trước đêm đầu hoặc ngay sau đêm cuối — một lượt lưu trú là một chuỗi đêm liền nhau. Để trống giá để giữ nguyên giá lượt này đang trả.
stay.nightDateMissing = Chọn đêm cần thêm.
stay.rateInvalid = Giá là số nguyên đồng.
eventType.booking.party_changed = Đã chuyển đặt phòng sang người khác
eventType.booking.notes_changed = Đã sửa ghi chú đặt phòng
eventType.booking.requests_changed = Đã thay đổi phòng trong đặt phòng
eventType.stay.rate_set = Đã đặt giá đêm
eventType.room.type_changed = Đã đổi loại phòng
eventType.setup.booking_source.defined = Đã tạo nguồn đặt phòng
eventType.setup.booking_source.updated = Đã cập nhật nguồn đặt phòng
eventType.setup.booking_source.retired = Đã ngừng dùng nguồn đặt phòng
error.guest.nothingToChange = Không có gì thay đổi.
error.contact.nothingToChange = Không có gì thay đổi.
error.setup.nothingToChange = Không có gì thay đổi.
error.stay.notEditable = Lượt lưu trú này đã kết thúc, không sửa đêm được nữa.
error.stay.nightPosted = Đêm này đã tính tiền. Huỷ khoản đó trên hoá đơn trước.
error.stay.nightNotFound = Lượt lưu trú này không giữ đêm đó.
error.stay.nightsNotContiguous = Một lượt lưu trú là một chuỗi đêm liền nhau. Để hở một đêm là thành hai lượt.
error.stay.nightsRequired = Lượt lưu trú cần ít nhất một đêm. Hãy huỷ, hoặc trả phòng cho khách.
error.stay.nothingToChange = Không có gì thay đổi.
```
