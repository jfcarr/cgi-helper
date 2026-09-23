#!/usr/bin/env python3

import os
import sys
from urllib.parse import parse_qs


class CGIHelperEnv:
    """
    Work with the environment, e.g., environment variables.
    """

    def __init__(self):
        self.env_vars = [
            "COMSPEC",
            "DOCUMENT_ROOT",
            "GATEWAY_INTERFACE",
            "HTTP_ACCEPT",
            "HTTP_ACCEPT_ENCODING",
            "HTTP_ACCEPT_LANGUAGE",
            "HTTP_CONNECTION",
            "HTTP_HOST",
            "HTTP_USER_AGENT",
            "PATH",
            "QUERY_STRING",
            "REMOTE_ADDR",
            "REMOTE_PORT",
            "REQUEST_METHOD",
            "REQUEST_URI",
            "SCRIPT_FILENAME",
            "SCRIPT_NAME",
            "SERVER_ADDR",
            "SERVER_ADMIN",
            "SERVER_NAME",
            "SERVER_PORT",
            "SERVER_PROTOCOL",
            "SERVER_SIGNATURE",
            "SERVER_SOFTWARE",
        ]

    def get_env_value(self, variable_name: str) -> str:
        """
        Get a single environment variable value, default to "UNAVAILABLE" if the value can't be found.
        """
        return os.environ.get(variable_name, "UNAVAILABLE")

    def dump_env(self):
        """
        Dump values of environment variables available to web server.
        """
        chh = CGIHelperHTML()

        print("<table>")
        for var_name in self.env_vars:
            print("<tr>")
            chh.write_tag("td", f"{var_name}:")
            chh.write_tag("td", f"{self.get_env_value(var_name)}")
            print("</tr>")
        print("</table>")


class CGIHelperForm:
    def parse_post_form(self, content_length, charset):
        """
        Parse the contents of a single-part posted form.
        """
        body = self.read_exact(content_length)

        return self.parse_urlencoded(body, charset=charset)

    def get_single_form_value(self, form, name, default=""):
        """
        Extract the value of a single posted form field.
        """
        vals = form.get(name)

        return vals[0] if vals else default

    def get_charset(self, content_type):
        """
        Find the character set in the content type text. Default to 'utf-8'.
        """
        charset = "utf-8"

        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("charset="):
                charset = part.split("=", 1)[1].strip().strip('"')
                break

        return charset

    def read_exact(self, n: int) -> bytes:
        """
        Read exactly n bytes from stdin (CGI provides Content-Length)
        """
        data = sys.stdin.buffer.read(n)

        if data is None:
            return b""

        return data

    def parse_urlencoded(self, body: bytes, charset: str = "utf-8"):
        """
        Decode form body and return a dictionary of the contents.
        """
        text = body.decode(charset, errors="replace")

        # parse_qs returns dict[str, list[str]]
        return {k: v for k, v in parse_qs(text, keep_blank_values=True).items()}

    def parse_querystring(self):
        """
        Parse the query string environment variable (populated from the query string part of the URL)
        and return a dictionary of the contents.
        """
        che = CGIHelperEnv()
        query_string = che.get_env_value("QUERY_STRING")
        data = parse_qs(query_string)

        return data

    def iterate_querystring_data(self, data):
        """
        Walk the query string dictionary and render the values as list entries.
        """
        chh = CGIHelperHTML()
        chh.start_unordered_list()
        for key, values in data.items():
            chh.write_tag("li", f"{key}: {values}")
        chh.end_unordered_list()


class CGIHelperHTML:
    """
    HTML-specific features, e.g., writing out HTML tags.
    """

    def start_html(self, title: str):
        """
        Start HTML content, including content type, opening head tag, and title.
        """
        print(
            f"Content-type:text/html\r\n\r\n<html>\n<head>\n<title>{title}</title>\n</head>\n<body>"
        )

    def end_html(self):
        """
        Conclude HTML content with closing body and html tags.
        """
        print("</body>\n</html>")

    def start_unordered_list(self):
        """
        Render starting tag of an unordered list.
        """
        print("<ul>")

    def end_unordered_list(self):
        """
        Render ending tag of an unordered list.
        """
        print("</ul>")

    def write_tag(self, tag_name: str, text: str):
        """
        Write an HTML tag, with content.
        """
        print(f"<{tag_name}>{text}</{tag_name}>")


class CGIUtil:
    @staticmethod
    def is_null_or_empty(value_to_check) -> bool:
        """
        Check to see if the specified value is NULL or empty.
        """
        return False if value_to_check is not None and value_to_check != "" else True


def self_test():
    """
    Exercise a series of CGI Helper functions.
    """
    chh = CGIHelperHTML()
    che = CGIHelperEnv()
    chf = CGIHelperForm()

    chh.start_html("CGI in Python")

    chh.write_tag("h2", "Greetings from CGI (in Python)")
    chh.write_tag("p", "Ready...")

    # Display all of the environment variables available to the CGI process.
    chh.write_tag("h2", "Environment Values")
    che.dump_env()

    request_method = che.get_env_value("REQUEST_METHOD")

    if request_method == "GET":
        chh.write_tag("h2", "Form GET")
        querystring_value = che.get_env_value("QUERY_STRING")
        if not CGIUtil.is_null_or_empty(querystring_value):
            data = chf.parse_querystring()
            chf.iterate_querystring_data(data)
        else:
            chh.write_tag(
                "p",
                "While the page was loaded with a GET, the query string is empty, so it looks like this was NOT a form GET",
            )

    if request_method == "POST":
        chh.write_tag("h2", "Form POST")

        content_type = che.get_env_value("CONTENT_TYPE")
        chh.write_tag("p", f"Content Type is {content_type}")

        content_length_raw = che.get_env_value("CONTENT_LENGTH")
        content_length = (
            0 if content_length_raw == "UNAVAILABLE" else int(content_length_raw)
        )

        # single-part form
        if content_type.startswith("application/x-www-form-urlencoded"):
            chh.write_tag("h3", "Single-Part Form")

            charset = chf.get_charset(content_type)
            chh.write_tag("p", f"Character Set is {charset}")

            form = chf.parse_post_form(content_length, charset)

            first_name = chf.get_single_form_value(form, "fname")
            last_name = chf.get_single_form_value(form, "lname")

            print("<table>")
            print("<tr>")
            chh.write_tag("td", f"First name is {first_name}")
            print("</tr>")
            print("<tr>")
            chh.write_tag("td", f"Last name is {last_name}")
            print("</tr>")
            print("</table>")

    chh.end_html()


def main():
    self_test()


if __name__ == "__main__":
    main()
