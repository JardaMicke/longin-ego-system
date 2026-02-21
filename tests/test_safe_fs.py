from longin_sdk.tools.fs import SafeFileSystem


def test_safe_fs_write_and_read(tmp_path) -> None:
    fs = SafeFileSystem(str(tmp_path))
    fs.write_file("a.txt", "hello")
    assert fs.read_file("a.txt") == "hello"
