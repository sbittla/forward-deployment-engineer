// Northwind edge agent (C++), runs on warehouse scanners with an RTC but no timezone database.
// Differs from the Java SDK in the canonical request itself.
#include <ctime>
#include <string>
#include "hmac_sha256.h"   // vendored
#include "base64.h"        // vendored

std::string canonical_request(const std::string& method, const std::string& encoded_path,
                              const std::string& canonical_query, const std::string& body, std::time_t now) {
    std::string body_hash = sha256_hex_upper(body);   // DIFFERENCE 1: UPPER-case hex body hash
    return to_upper(method) + "\n" + encoded_path + "\n" + canonical_query + "\n" + body_hash + "\n"
         + std::to_string(static_cast<long long>(now)); // DIFFERENCE 2: unix epoch seconds, not ISO basic
}

// Signature and headers are identical to the Java SDK: base64(HMAC-SHA256(secret, canonical)),
// "Authorization: NWS1-HMAC-SHA256 Credential=<key>, Signature=<sig>", "X-NWS-Date: <same timestamp string>".
