import json

TUTORIAL = {
    "Version": "2012-10-17",
    "Statement": [
        {"Effect": "Allow", "Action": "*", "Resource": "*"},
        {"Effect": "Allow", "Action": ["s3:*", "s3:GetObject"], "Resource": "arn:aws:s3:::docs/*"},
        {"Effect": "Allow", "NotAction": "iam:*", "Resource": "*"},
        {"Effect": "Allow", "Principal": {"AWS": "*"}, "Action": "s3:GetObject", "Resource": "arn:aws:s3:::docs/*"},
        {"Effect": "Allow", "Action": ["ec2:DescribeInstances", "s3:ListAllMyBuckets"], "Resource": "*"},
        {"Effect": "Deny", "Action": "*", "Resource": "*"},
    ],
}


def test_lint_policy(impl):
    assert sorted(impl.lint_policy(TUTORIAL)) == sorted([
        "wildcard-action:*", "wildcard-resource", "wildcard-action:s3:*", "not-action", "public-principal"])


def test_read_only_wildcard_resource_ok(impl):
    p = {"Statement": [{"Effect": "Allow", "Action": ["ec2:DescribeInstances"], "Resource": "*"}]}
    assert impl.lint_policy(p) == []


def test_generate(impl):
    needs = [
        ("s3:GetObject", "arn:aws:s3:::docs/*"),
        ("dynamodb:PutItem", "arn:aws:dynamodb:us-east-1:111122223333:table/embeddings"),
        ("s3:ListBucket", "arn:aws:s3:::docs"),
        ("dynamodb:GetItem", "arn:aws:dynamodb:us-east-1:111122223333:table/embeddings"),
        ("dynamodb:PutItem", "arn:aws:dynamodb:us-east-1:111122223333:table/embeddings"),
    ]
    p = impl.generate_policy(needs)
    assert p["Version"] == "2012-10-17"
    assert p["Statement"] == [
        {"Sid": "S1", "Effect": "Allow", "Action": ["s3:GetObject"], "Resource": "arn:aws:s3:::docs/*"},
        {"Sid": "S2", "Effect": "Allow", "Action": ["dynamodb:GetItem", "dynamodb:PutItem"],
         "Resource": "arn:aws:dynamodb:us-east-1:111122223333:table/embeddings"},
        {"Sid": "S3", "Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": "arn:aws:s3:::docs"},
    ]
    assert impl.lint_policy(p) == []


def test_lint_terraform(impl):
    bad = {"resource": {"aws_s3_bucket": {"docs": {}, "logs": {}},
                        "aws_s3_bucket_versioning": {"v": {"bucket": "${aws_s3_bucket.docs.id}",
                                                           "versioning_configuration": {"status": "Suspended"}}},
                        "aws_s3_bucket_public_access_block": {"p": {
                            "bucket": "${aws_s3_bucket.docs.id}", "block_public_acls": True,
                            "block_public_policy": True, "ignore_public_acls": True, "restrict_public_buckets": False}}}}
    assert sorted(impl.lint_terraform(bad)) == sorted([
        "sse:docs", "versioning:docs", "public-access:docs", "sse:logs", "versioning:logs", "public-access:logs"])


def test_your_infra(impl, exercise_dir):
    doc = json.loads((exercise_dir / "infra.tf.json").read_text())
    assert "docs" in doc["resource"]["aws_s3_bucket"]
    assert impl.lint_terraform(doc) == []
