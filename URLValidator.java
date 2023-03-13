// Programa Java para verificar si una URL es válida usando
// regular expression por owasp
import java.util.regex.Matcher;
import java.util.regex.Pattern;
class URLValidator {
    /*expresión regular*/
    private static final String URL_REGEX =
            "^((((https?|ftps?|gopher|telnet|nntp)://)|(mailto:|news:))" +
                    "(%{2}|[-()_.!~*';/?:@&=+$, A-Za-z0-9])+)" + "([).!';/?:, ][[:blank:]])?$";
    private static final Pattern URL_PATTERN = Pattern.compile(URL_REGEX);
    public static boolean urlValidator(String url)
    {
        if (url == null) {
            return false;
        }
        Matcher matcher = URL_PATTERN.matcher(url);
        return matcher.matches();
    }
    public static void main(String[] args)
    {
        String url = "https://files.sld.cu/dne/files/2012/03/vol1_iv.pdf";
        /* validar la url */
        if (urlValidator(url))
            System.out.print("La url dada " + url + " es válida");
        else
            System.out.print("La url dada " + url + " no es válida");
    }
}