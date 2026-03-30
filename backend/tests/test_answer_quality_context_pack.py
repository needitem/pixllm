from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.chat.answer_quality import build_context_pack


def _result_entry(text: str, path: str) -> dict:
    return {
        "payload": {
            "text": text,
            "source_file": path,
            "file_path": path,
            "line_start": 1,
            "line_end": 1,
        }
    }


def test_question_about_ui_flow_does_not_mark_framework_terms_as_settings() -> None:
    question = "이 창 초기화 흐름이 어떻게 되나?"
    pack = build_context_pack(
        results=[
            _result_entry(
                "InitializeComponent(); var dialog = new OpenFileDialog(); layer.LayerVisible = true;",
                "/repo/ui/MainWindow.xaml.cs",
            )
        ],
        sources=[],
        response_type="code_explain",
        execution_plan={"question": question},
    )

    assert pack["settings"] == []


def test_question_about_configuration_keeps_generic_settings_signal() -> None:
    question = "이 서비스는 옵션을 어떻게 등록하고 바인딩하나?"
    pack = build_context_pack(
        results=[
            _result_entry(
                "services.Configure<AppOptions>(configuration); options.Bind(configuration.GetSection(\"App\")); register_pipeline(builder);",
                "/repo/app/bootstrap.py",
            )
        ],
        sources=[],
        response_type="code_explain",
        execution_plan={"question": question},
    )

    assert len(pack["settings"]) == 1
    assert pack["settings"][0]["path"] == "/repo/app/bootstrap.py"


def test_question_about_file_io_does_not_create_settings_bias() -> None:
    question = "파일 읽기와 파싱 흐름은 어떻게 되나?"
    pack = build_context_pack(
        results=[
            _result_entry(
                "reader = Parser(); payload = reader.parse(stream.read()); return payload",
                "/repo/app/io/parser.py",
            )
        ],
        sources=[],
        response_type="code_explain",
        execution_plan={"question": question},
    )

    assert pack["settings"] == []
