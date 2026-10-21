// Northwind dispatch service (Go). Same canonical request as the Java SDK, but note the two differences
// in how the result is encoded and sent.
package signer

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"net/http"
	"time"
)

// Sign adds auth headers to req. canonical is built exactly like CustomerSigner.canonicalRequest (Java).
func Sign(req *http.Request, canonical string, keyID, secret string, ts time.Time) {
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(canonical))
	sig := hex.EncodeToString(mac.Sum(nil)) // DIFFERENCE 1: lowercase hex, not base64

	// DIFFERENCE 2: header names are written in lower case (HTTP/2 style) by this service.
	req.Header["authorization"] = []string{"NWS1-HMAC-SHA256 Credential=" + keyID + ", Signature=" + sig}
	req.Header["x-nws-date"] = []string{ts.UTC().Format("20060102T150405Z")}
}
