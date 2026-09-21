"""core/response.py：统一响应体的结构契约 {code, message, data}。不依赖任何外部服务。"""

from app.core.response import fail, ok, ok_page


def test_ok_default_structure():
    assert ok() == {"code": 0, "message": "success", "data": None}


def test_ok_keeps_payload_and_message():
    assert ok({"a": 1}) == {"code": 0, "message": "success", "data": {"a": 1}}
    assert ok(message="ok") == {"code": 0, "message": "ok", "data": None}


def test_ok_page_nests_pagination_fields():
    assert ok_page([{"id": 1}], total=1, page=2, page_size=20) == {
        "code": 0,
        "message": "success",
        "data": {"items": [{"id": 1}], "total": 1, "page": 2, "page_size": 20},
    }


def test_ok_page_accepts_empty_items():
    assert ok_page([], total=0, page=1, page_size=20)["data"]["items"] == []


def test_fail_always_has_null_data():
    assert fail(404, "订单不存在") == {"code": 404, "message": "订单不存在", "data": None}


def test_all_helpers_share_the_same_keys():
    keys = ("code", "message", "data")
    assert tuple(ok()) == keys
    assert tuple(ok_page([], 0, 1, 20)) == keys
    assert tuple(fail(500, "x")) == keys