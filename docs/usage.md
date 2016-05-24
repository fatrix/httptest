The HTTPTest Tool helps to send various **requests** to multiple **environments**. For example, you want to test the following URLs:

    GET http://test.example.com/blog HTTP/1.1                (200 expected)
    GET http://test.example.com/private HTTP/1.1             (301 expected)
    
    GET https://test.example.com/private HTTP/1.1            (200 expected)
    GET https://test.example.com/blog HTTP/1.1               (301 expected)

    GET http://example.com/blog HTTP/1.1                     (200 expected)
    GET http://example.com/private HTTP/1.1                  (301 expected)
    
    GET https://example.com/private HTTP/1.1                 (200 expected)
    GET https://example.com/blog HTTP/1.1                    (301 expected)

The following configuration would achieve this.

    environments:
        - name:      test
          base_url:  http://test.example.com
        - name:      public
          base_url:  http://example.com
        - name:      test-ssl
          base_url:  https://test.example.com
        - name:      public-ssl
          base_url:  https://example.com
    tests:
        - name:     test_blog
          uri:      /blog
          asserts:
              assert_status_code_is: 200
              assert_body_contains:  "My Blog"
        - name:     test_private
          uri:      /private
          asserts:
              assert_status_code_is: 301
              assert_body_contains:  "Login"

## Configuration

### environment

#### name

The environment's `name`.

#### base_url

`base_url` gets prepended to the `uri` in the test definition.

### tests

The array tests contains the definition of test cases.

#### name

The `name` must start with `test_`.

#### uri

The path to send the request to.

#### method

Default: `GET`

If POST, you can define the data (JSON format) in the key `data`. If the data is recognized as URL (starting with http), the data is loaded from this URL.

### skip

With the key `skip` the entire request or all requests to an environment will be skipped. A value is optional and can contain any reason.

### ssl_verify

`ssl_verify` disables SSL certificate check.

### timeout

Value in seconds. Default is 10 seconds. `timeout` must be less than 20s.

### headers

Custom headers as key/value to send with the request.

     headers:
        MY-1HEADER: headers value
        MY-2HEADER: headers value

### asserts
#### assert_status_code_is
#### assert_status_code_is_not
#### assert_header_is_set
#### assert_header_is_not_set
#### assert_header_value_contains
#### assert_header_value_not_contains
#### assert_body_contains
#### assert_is_json
