"""Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""
"""Tests for jws."""

__author__ = 'quannguyen@google.com (Quan Nguyen)'

import json
import test_vector
import unittest
from jwt import jwt
from jws import jws
import test_util
from jws.cleartext_jwk_set_reader import CleartextJwkSetReader
import calendar
import datetime


# TODO(quannguyen): add more tests.
class JwtTest(unittest.TestCase):

  def test_jwt_claims_issuer_subject_audiences(self):
    # Sign
    priv_key = CleartextJwkSetReader.from_json(test_vector.json_rsa_priv_key)
    signer = jws.JwsPublicKeySign(priv_key)
    signed_token = signer.sign(test_vector.test_header_rsa,
                               test_vector.test_payload)

    # Verify
    pub_key = CleartextJwkSetReader.from_json(test_vector.json_rsa_pub_key)
    # Ignore issuer, subject and audience.
    verifier = jwt.JwtPublicKeyVerify(pub_key)
    self.assertTrue(verifier.verify(signed_token))
    # Correct issuer, subject and audience.
    verifier = jwt.JwtPublicKeyVerify(pub_key, 'issuer1', 'subject1',
                                      ['aud1', 'aud2'])
    self.assertTrue(verifier.verify(signed_token))
    # Modify token.
    for modified_token in test_util.modify_token(signed_token):
      self.assertFalse(verifier.verify(modified_token))

    # Incorrect issuer.
    verifier = jwt.JwtPublicKeyVerify(pub_key, 'issuer0', 'subject1', ['aud1'])
    self.assertFalse(verifier.verify(signed_token))
    # Incorrect subject.
    verifier = jwt.JwtPublicKeyVerify(pub_key, 'issuer1', 'subject0', ['aud1'])
    self.assertFalse(verifier.verify(signed_token))
    # Incorrect audience.
    verifier = jwt.JwtPublicKeyVerify(pub_key, 'issuer1', 'subject1', ['aud'])
    self.assertFalse(verifier.verify(signed_token))

  def test_jwt_claims_exp_nbf(self):
    # Sign
    priv_key = CleartextJwkSetReader.from_json(test_vector.json_rsa_priv_key)
    signer = jws.JwsPublicKeySign(priv_key)
    # Valid exp time.
    payload = json.loads(test_vector.test_payload)
    payload['exp'] = _get_unix_timestamp() + 100
    payload = json.dumps(payload)
    signed_token = signer.sign(test_vector.test_header_rsa, payload)

    # Verify
    pub_key = CleartextJwkSetReader.from_json(test_vector.json_rsa_pub_key)
    verifier = jwt.JwtPublicKeyVerify(pub_key)
    self.assertTrue(verifier.verify(signed_token))

    # Invalid exp time.
    payload = json.loads(test_vector.test_payload)

    payload['exp'] = _get_unix_timestamp() - 100
    payload = json.dumps(payload)
    signed_token = signer.sign(test_vector.test_header_rsa, payload)

    # Verify
    self.assertFalse(verifier.verify(signed_token))

    # Valid nbf time.
    payload = json.loads(test_vector.test_payload)

    payload['nbf'] = _get_unix_timestamp() - 100
    payload = json.dumps(payload)
    signed_token = signer.sign(test_vector.test_header_rsa, payload)

    # Verify
    self.assertTrue(verifier.verify(signed_token))

    # Invalid nbf time.
    payload = json.loads(test_vector.test_payload)

    payload['nbf'] = _get_unix_timestamp() + 100
    payload = json.dumps(payload)
    signed_token = signer.sign(test_vector.test_header_rsa, payload)

    # Verify
    self.assertFalse(verifier.verify(signed_token))


def _get_unix_timestamp():
  return calendar.timegm(datetime.datetime.utcnow().utctimetuple())


if __name__ == '__main__':
  unittest.main()
