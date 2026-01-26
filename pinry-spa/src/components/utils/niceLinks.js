import DOMPurify from 'dompurify';

const encoder = document.createElement('div');
function escapeHTML(text) {
  encoder.innerText = text;
  return encoder.innerHTML;
}

// Configure DOMPurify to allow only safe tags and attributes
const DOMPURIFY_CONFIG = {
  ALLOWED_TAGS: ['a', 'b', 'i', 'em', 'strong', 'br'],
  ALLOWED_ATTR: ['href', 'target', 'rel'],
  ALLOW_DATA_ATTR: false,
  ADD_ATTR: ['rel'], // Will be added to all links
};

const reURL = /https?:[/][/](?:www[.])?([^/]+)(?:[/]([.]?[^\s,.<>])+)?/g;

function niceLinks(text) {
  if (!text) return '';

  // First escape HTML to prevent XSS
  const escaped = escapeHTML(text);

  // Then convert URLs to links
  const withLinks = escaped.replace(
    reURL,
    '<a href="$&" target="_blank" rel="noopener noreferrer">$1</a>',
  );

  // Finally sanitize with DOMPurify as defense in depth
  return DOMPurify.sanitize(withLinks, DOMPURIFY_CONFIG);
}

export default niceLinks;
