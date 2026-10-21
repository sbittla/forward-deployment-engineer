// Northwind Logistics SDK, request signing (Java). Reference implementation from the customer's repo.
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public final class CustomerSigner {
    static final DateTimeFormatter BASIC = DateTimeFormatter.ofPattern("yyyyMMdd'T'HHmmss'Z'").withZone(ZoneOffset.UTC);

    // RFC 3986 encoding: URLEncoder is form-encoding, so patch the three differences.
    static String encode(String s) {
        return URLEncoder.encode(s, StandardCharsets.UTF_8)
                .replace("+", "%20").replace("*", "%2A").replace("%7E", "~");
    }

    static String encodePath(String path) {
        StringBuilder out = new StringBuilder();
        for (String seg : path.split("/", -1)) {
            if (out.length() > 0 || path.startsWith("/")) out.append("/");
            out.append(encode(seg));
        }
        String r = out.toString();
        return r.startsWith("//") ? r.substring(1) : r;
    }

    static String canonicalQuery(Map<String, List<String>> query) {
        List<String> pairs = new ArrayList<>();
        for (Map.Entry<String, List<String>> e : query.entrySet())
            for (String v : e.getValue()) pairs.add(encode(e.getKey()) + "=" + encode(v));
        Collections.sort(pairs);                       // sort the *encoded* pairs, byte order
        return String.join("&", pairs);
    }

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x));
        return sb.toString();
    }

    public static String canonicalRequest(String method, String path, Map<String, List<String>> query,
                                          byte[] body, ZonedDateTime ts) throws Exception {
        String bodyHash = hex(MessageDigest.getInstance("SHA-256").digest(body));
        return method.toUpperCase() + "\n" + encodePath(path) + "\n" + canonicalQuery(query) + "\n"
                + bodyHash + "\n" + BASIC.format(ts);
    }

    public static String sign(String canonical, String secret) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        return Base64.getEncoder().encodeToString(mac.doFinal(canonical.getBytes(StandardCharsets.UTF_8)));
    }

    // Prints test vectors: canonical request (escaped) and signature.
    public static void main(String[] args) throws Exception {
        ZonedDateTime ts = ZonedDateTime.of(2026, 10, 16, 9, 30, 0, 0, ZoneOffset.UTC);
        Map<String, List<String>> q1 = new TreeMap<>();
        q1.put("status", List.of("open"));
        q1.put("limit", List.of("50"));
        Map<String, List<String>> q2 = new TreeMap<>();
        q2.put("q", List.of("late delivery *urgent*", "a~b"));
        q2.put("customer name", List.of("O'Brien & Sons"));
        Object[][] cases = {
            {"get", "/v1/shipments", q1, "".getBytes(StandardCharsets.UTF_8)},
            {"POST", "/v1/shipments/SH 42/notes", q2, "{\"note\":\"Ünïcödé ok\"}".getBytes(StandardCharsets.UTF_8)},
        };
        for (Object[] c : cases) {
            @SuppressWarnings("unchecked")
            String canon = canonicalRequest((String) c[0], (String) c[1], (Map<String, List<String>>) c[2], (byte[]) c[3], ts);
            System.out.println(canon.replace("\n", "\\n"));
            System.out.println(sign(canon, "s3cr3t-key"));
        }
    }
}
