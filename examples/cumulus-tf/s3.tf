# bucket - internal
resource "aws_s3_bucket" "internal" {
   bucket = "${local.ec2_resources_name}-internal"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "internal-acl" {
   bucket = aws_s3_bucket.internal.id
   acl = "private"
   depends_on = [aws_s3_bucket_ownership_controls.internal_acl_ownership]
}

resource "aws_s3_bucket_ownership_controls" "internal_acl_ownership" {
   bucket = aws_s3_bucket.internal.id
   rule {
     object_ownership = "ObjectWriter"
   }
}

# bucket - public
resource "aws_s3_bucket" "public" {
   bucket = "${local.ec2_resources_name}-public"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "public-acl" {
   bucket = aws_s3_bucket.public.id
   acl = "private"
   depends_on = [aws_s3_bucket_ownership_controls.public_acl_ownership]
}

resource "aws_s3_bucket_ownership_controls" "public_acl_ownership" {
   bucket = aws_s3_bucket.public.id
   rule {
     object_ownership = "ObjectWriter"
   }
}

# bucket - private
resource "aws_s3_bucket" "private" {
   bucket = "${local.ec2_resources_name}-private"
  force_destroy = true
}

resource "aws_s3_bucket_policy" "allow_gitc_read" {
   bucket = aws_s3_bucket.private.id
   policy = data.aws_iam_policy_document.allow_access_from_gitc.json
}

data "aws_iam_policy_document" "allow_access_from_gitc" {
  statement {
    principals {
      type        = "AWS"
      identifiers = [var.gibs_account_id == "mocked" ? local.account_id : var.gibs_account_id, local.account_id]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.private.arn,
      "${aws_s3_bucket.private.arn}/*"
    ]
  }
}

resource "aws_s3_bucket_acl" "private-acl" {
   bucket = aws_s3_bucket.private.id
   acl = "private"
   depends_on = [aws_s3_bucket_ownership_controls.private_acl_ownership]
}

resource "aws_s3_bucket_ownership_controls" "private_acl_ownership" {
   bucket = aws_s3_bucket.private.id
   rule {
     object_ownership = "ObjectWriter"
   }
}

resource "aws_s3_bucket" "protected" {
   bucket = "${local.ec2_resources_name}-protected"
  force_destroy = true
}

resource "aws_s3_bucket_acl" "protected-acl" {
   bucket = aws_s3_bucket.protected.id
   acl = "private"
   depends_on = [aws_s3_bucket_ownership_controls.protected_acl_ownership]
}

resource "aws_s3_bucket_ownership_controls" "protected_acl_ownership" {
   bucket = aws_s3_bucket.protected.id
   rule {
     object_ownership = "ObjectWriter"
   }
}
