import pulumi
import pulumi_aws as aws
import os

bucket = aws.s3.Bucket('my-bucket')
filepath = os.path.join('website', 'index.html')
obj = aws.s3.BucketObject('index.html',
  bucket=bucket,
  source=pulumi.FileAsset(filepath)
)

pulumi.export('bucket_name', bucket.bucket)