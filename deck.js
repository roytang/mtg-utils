document.write('<h4><a href=\"{{ deck_url }}\">{{ d.title|escape|jquote }}</a> - a deck for {{ d.format_desc }} by {{ d.author_nick }}</h4>');
document.write('{{ d.render|jquote }}');
document.write('<span>Powered by <a href="{{ home_url }}">Decklist Sharing Tool</a></span>');

