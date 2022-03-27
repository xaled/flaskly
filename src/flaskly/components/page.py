from abc import ABC, abstractmethod
from html import escape as html_escape

from flaskly.globals import current_flaskly_app as _app
from flaskly.includes import reduce_includes, ComponentIncludes
from flaskly.typing import Optional, Dict, PageResponse, RenderReturnValue
from .component import AbstractComponent

META_TAGS_KEYS = ('description', 'keywords', 'author', 'viewport')


class AbstractPage(AbstractComponent, ABC):
    title: Optional[str] = None
    description: Optional[str] = None
    meta_tags: Optional[Dict] = None
    status_code: Optional[int] = None
    additional_includes: ComponentIncludes = None
    _reduced_includes = None

    def render(self, **options) -> RenderReturnValue:
        response = options.get('page_response', None)
        return '<!DOCTYPE html><html>' + self.render_head_tag(response) + self.render_body_tag(**options) + '</html>'

    @classmethod
    def reduce_includes(cls):
        if getattr(cls, '_reduced_includes', None) is None:
            cls._reduced_includes = reduce_includes(getattr(_app.config, 'default_includes', None),
                                                    cls.additional_includes)

        return cls._reduced_includes

    def render_head_tag(self, page_response: PageResponse = None) -> str:
        head = "<head>"

        # Charset
        head += '<meta charset="UTF-8">'

        # Fav icons
        if hasattr(_app.config, 'icons'):
            for icon in _app.config.icons:
                head += icon.rendered

        # Title
        title = page_response.title if page_response and page_response.title is not None else \
            self.title if self.title is not None else getattr(_app.config, 'default_title', None)
        if title is not None:
            head += f'<title>{html_escape(title)}</title>'

        # Meta tags
        for meta in META_TAGS_KEYS:
            if page_response and getattr(page_response.meta_tags, meta, None) is not None:
                meta_value = page_response.meta_tags[meta]
            elif self.meta_tags is not None and getattr(self.meta_tags, meta, None) is not None:
                meta_value = self.meta_tags[meta]
            else:
                meta_value = getattr(_app.config.default_meta_tags, meta, None)
            if meta_value:
                head += f'<meta name="{meta}" content="{html_escape(meta_value)}">'

        # Head includes
        head += self.reduce_includes().render_head_includes()

        head += "</head>"
        return head

    def render_body_tag(self, **options) -> RenderReturnValue:
        # body = '<body>'
        #
        # # Page content
        # body += self.render_page_content(**options)
        #
        #
        # # Body includes
        # body += self.reduce_includes().render_body_includes()
        # body += '</body>'
        #
        # # Render Layout
        # rendered_content = self.render_page_content(**options)
        #
        #
        # return body
        return '<body>' + self.render_page_content(**options) + \
               self.reduce_includes().render_body_includes() + '</body>'

    @abstractmethod
    def render_page_content(self, **options) -> RenderReturnValue:
        raise NotImplementedError()
