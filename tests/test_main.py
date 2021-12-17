from app import main


def test__templates():
    main.templates.get_template(
        "index.html"
    ), "Assert jinja2.exceptions.TemplateNotFound is not thrown"
