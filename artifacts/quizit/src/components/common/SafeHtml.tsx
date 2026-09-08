import { useMemo } from "react";
import DOMPurify from "dompurify";

interface Props {
  html: string;
  className?: string;
}

const ASSET_HOST = "https://www.indiabix.com";

/** IndiaBix's math notation (fractions, brackets, root signs) ships as tiny relative-path
 * images and marked-up tables — rewrite `/_files/...` src attributes to absolute URLs so
 * they actually load (credit: IndiaBix, see footer). */
DOMPurify.addHook("afterSanitizeAttributes", (node) => {
  if (node.tagName === "IMG") {
    const src = node.getAttribute("src");
    if (src && src.startsWith("/")) {
      node.setAttribute("src", `${ASSET_HOST}${src}`);
    }
    node.setAttribute("loading", "lazy");
  }
});

/**
 * Renders HTML content safely using DOMPurify to sanitize and prevent XSS.
 * Allows images, links, basic formatting, and the small answer-notation tables
 * IndiaBix uses for fractions/expressions — blocks scripts and everything else.
 */
export function SafeHtml({ html, className = "" }: Props) {
  const sanitized = useMemo(() => {
    const config = {
      ALLOWED_TAGS: [
        "p", "br", "strong", "em", "u", "i", "b", "sup", "sub", "a", "img",
        "div", "span", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6",
        "table", "thead", "tbody", "tr", "td", "th",
      ],
      ALLOWED_ATTR: ["src", "alt", "href", "title", "class", "id", "style", "width", "height", "align", "rowspan", "colspan", "cellpadding", "cellspacing"],
      ALLOW_DATA_ATTR: false,
      KEEP_CONTENT: true,
    };
    return DOMPurify.sanitize(html, config);
  }, [html]);

  return (
    <div
      className={`indiabix-html ${className}`}
      dangerouslySetInnerHTML={{ __html: sanitized }}
    />
  );
}
