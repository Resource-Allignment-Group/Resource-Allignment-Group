import io
from bson import ObjectId
from PIL import Image
import struct, zlib

# Tests for file upload/download endpoints and their DB methods

### Create mock files to use for testing

def make_fake_image():
    """Creates a minimal valid 1x1 PNG in memory"""
    def png_chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = png_chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff"))
    iend = png_chunk(b"IEND", b"")
    return io.BytesIO(sig + ihdr + idat + iend)

def make_fake_pdf():
    """Creates a minimal valid PDF in memory"""
    content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF"
    return io.BytesIO(content)

### Equipment images -----------------------------------------

def test_upload_equipment_image(login_admin):
    img = make_fake_image()
    res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "image",
            "file": (img, "test.png"),
        },
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is True
    assert "file_id" in res.get_json()

def test_upload_equipment_image_wrong_type(login_admin):
    # Non-image file should be rejected
    res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "image",
            "file": (io.BytesIO(b"not an image"), "test.txt"),
        },
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is False

def test_upload_equipment_image_not_admin(login_user):
    img = make_fake_image()
    res = login_user.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "image",
            "file": (img, "test.png"),
        },
        content_type="multipart/form-data",
    )
    assert res.status_code in (403, 200)
    if res.status_code == 200:
        assert res.get_json()["result"] is False

def test_get_equipment_image(login_admin):
    img = make_fake_image()
    upload_res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "image",
            "file": (img, "test.png"),
        },
        content_type="multipart/form-data",
    )
    file_id = upload_res.get_json()["file_id"]
    res = login_admin.get(f"/get_equipment_image/000000000000000000000001/{file_id}")
    assert res.status_code == 200
    assert res.content_type == "image/png"

def test_get_equipment_image_not_found(login_user):
    res = login_user.get(
        f"/get_equipment_image/000000000000000000000001/nonexistent_id"
    )
    assert res.status_code == 404

def test_remove_equipment_image(login_admin):
    img = make_fake_image()
    upload_res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "image",
            "file": (img, "test.png"),
        },
        content_type="multipart/form-data",
    )
    file_id = upload_res.get_json()["file_id"]
    res = login_admin.post(
        "/remove_equipment_file",
        json={
            "equipment_id": "000000000000000000000001",
            "file_id": file_id,
            "file_type": "image",
        },
    )
    assert res.get_json()["result"] is True

def test_set_equipment_display_image(login_admin):
    img = make_fake_image()
    upload_res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "image",
            "file": (img, "test.png"),
        },
        content_type="multipart/form-data",
    )
    file_id = upload_res.get_json()["file_id"]
    res = login_admin.post(
        "/set_equipment_display_image",
        json={"equipment_id": "000000000000000000000001", "image_id": file_id},
    )
    assert res.get_json()["result"] is True

### Equipment reports -----------------------------------------

def test_upload_equipment_report(login_admin):
    pdf = make_fake_pdf()
    res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "report",
            "file": (pdf, "test.pdf"),
        },
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is True

def test_upload_equipment_report_wrong_type(login_admin):
    res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "report",
            "file": (io.BytesIO(b"not a pdf"), "test.txt"),
        },
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is False

def test_get_equipment_report(login_admin):
    pdf = make_fake_pdf()
    upload_res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "report",
            "file": (pdf, "test.pdf"),
        },
        content_type="multipart/form-data",
    )
    file_id = upload_res.get_json()["file_id"]
    res = login_admin.get(
        f"/get_equipment_report/000000000000000000000001/{file_id}"
    )
    assert res.status_code == 200
    assert res.content_type == "application/pdf"

def test_remove_equipment_report(login_admin):
    pdf = make_fake_pdf()
    upload_res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "report",
            "file": (pdf, "test.pdf"),
        },
        content_type="multipart/form-data",
    )
    file_id = upload_res.get_json()["file_id"]
    res = login_admin.post(
        "/remove_equipment_file",
        json={
            "equipment_id": "000000000000000000000001",
            "file_id": file_id,
            "file_type": "report",
        },
    )
    assert res.get_json()["result"] is True

### Profile images -----------------------------------------

def test_upload_profile_image(login_user):
    img = make_fake_image()
    res = login_user.post(
        "/upload_profile_image",
        data={"file": (img, "profile.png")},
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is True

def test_upload_profile_image_wrong_type(login_user):
    res = login_user.post(
        "/upload_profile_image",
        data={"file": (io.BytesIO(b"not an image"), "profile.txt")},
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is False

def test_get_profile_image(login_user):
    img = make_fake_image()
    login_user.post(
        "/upload_profile_image",
        data={"file": (img, "profile.png")},
        content_type="multipart/form-data",
    )
    db = login_user.application.db
    user = db.get_user_by_email("user@gmail.com")
    res = login_user.get(f"/get_profile_image/{str(user.id)}")
    assert res.status_code == 200
    assert res.content_type == "image/png"

def test_get_profile_image_not_found(login_user):
    res = login_user.get(f"/get_profile_image/{str(ObjectId())}")
    assert res.status_code == 404

def test_delete_profile_image(login_user):
    img = make_fake_image()
    login_user.post(
        "/upload_profile_image",
        data={"file": (img, "profile.png")},
        content_type="multipart/form-data",
    )
    res = login_user.post("/delete_profile_image")
    assert res.get_json()["result"] is True

def test_delete_profile_image_none_set(login_user):
    # No profile image uploaded — should return False
    res = login_user.post("/delete_profile_image")
    assert res.get_json()["result"] is False

### File Upload Edge Cases -----------------------------------------

def test_upload_equipment_file_invalid_type(login_admin):
    img_buf = io.BytesIO()
    Image.new("RGB", (10, 10)).save(img_buf, format="PNG")
    img_buf.seek(0)
    res = login_admin.post(
        "/upload_equipment_file",
        data={
            "equipment_id": "000000000000000000000001",
            "file_type": "invalid_type",
            "file": (img_buf, "test.png"),
        },
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is False

def test_upload_equipment_file_no_file(login_admin):
    res = login_admin.post(
        "/upload_equipment_file",
        data={"equipment_id": "000000000000000000000001", "file_type": "image"},
        content_type="multipart/form-data",
    )
    assert res.get_json()["result"] is False

def test_set_display_image_wrong_image_id(login_admin):
    # Image ID not in the equipment's images list — should fail
    res = login_admin.post("/set_equipment_display_image", json={
        "equipment_id": "000000000000000000000001",
        "image_id": "nonexistent_image_id",
    })
    assert res.get_json()["result"] is False

def test_remove_equipment_file_invalid_type(login_admin):
    res = login_admin.post("/remove_equipment_file", json={
        "equipment_id": "000000000000000000000001",
        "file_id": "someid",
        "file_type": "invalid_type",
    })
    assert res.get_json()["result"] is False

def test_remove_equipment_file_not_found(login_admin):
    # Valid type but file_id doesn't exist on the equipment
    res = login_admin.post("/remove_equipment_file", json={
        "equipment_id": "000000000000000000000001",
        "file_id": "nonexistent_id",
        "file_type": "image",
    })
    assert res.get_json()["result"] is False