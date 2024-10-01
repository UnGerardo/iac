import pulumi
import pulumi_aws as aws
import os
import mimetypes

config = pulumi.Config();
websiteDir = config.require('siteDir')

bucket = aws.s3.BucketV2('web-bucket')

bucketWebConfig = aws.s3.BucketWebsiteConfigurationV2('s3-website',
  bucket=bucket.bucket,
  index_document={
    'suffix': 'index.html'
  }
)

bucketPublicAccessBlock = aws.s3.BucketPublicAccessBlock('public-access-block',
  bucket=bucket.bucket,
  block_public_acls=False
)

for file in os.listdir(websiteDir):
  filePath = os.path.join(websiteDir, file)
  mimetype, _ = mimetypes.guess_type(filePath)
  obj = aws.s3.BucketObject(file,
    bucket=bucket.id,
    source=pulumi.FileAsset(filePath),
    content_type=mimetype
  )

bucketPolicy = aws.s3.BucketPolicy('bucket-policy',
  bucket=bucket.id,
  opts=pulumi.ResourceOptions(depends_on=[bucketPublicAccessBlock]),
  policy=pulumi.Output.json_dumps({
    'Version': '2012-10-17',
    'Statement': [
      {
        'Effect': 'Allow',
        'Principal': '*',
        'Action': ['s3:GetObject'],
        'Resource': [
          pulumi.Output.format('arn:aws:s3:::{0}/*', bucket.id)
        ]
      }
    ]
  })
)

pulumi.export('bucket_name', bucket.id)
pulumi.export('website_url', pulumi.Output.concat('http://', bucketWebConfig.website_endpoint))