The HTTPTest Tool sends different **tests** requests to multiple **environments**. For example, you are hosting a website with a blog and a private section. For testing purposes you deployed a version available under test.example.com and the real site under example.com. You need to test the correct behaviour of the different instances and their configuration.

The following URLs needs to be tested:

    GET http://test.example.com/blog HTTP/1.1
    GET http://test.example.com/private HTTP/1.1
    
    GET https://test.example.com/private HTTP/1.1
    GET https://test.example.com/blog HTTP/1.1

    GET http://example.com/blog HTTP/1.1
    GET http://example.com/private HTTP/1.1
    
    GET https://example.com/private HTTP/1.1
    GET https://example.com/blog HTTP/1.1


The following configuration would describe the test run.

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

The configuration can be written in YAML or JSON format.

### environment

#### name

The environment's `name`.

#### base_url

`base_url` gets prepended to the `uri` in the test definition.

#### variables

Environment specific values in URI's can be set per environment as variables:

For environment `A`:

    variables:
        KEY: 1234

For environment `B`:

    variables:
        KEY: 5678

`uri` in test:

    uri: /api/key/{% verbatim %}{{KEY}}{% endverbatim %}

### tests

The array tests contains the definition of test cases.

#### name

The `name` must start with `test_`.

#### uri

The path to send the request to.

#### method

Default: `GET`

If `POST`, you can define the data (JSON format) in the key `data`. If the data is recognized as URL (starting with `http`), the data is loaded from this URL. The data is sent with Content-Type `application/xml` if the string starts with `<`.

### skip

With the key `skip` the entire request or all requests to an environment will be skipped. A value is optional and can contain any reason.

### ssl_verify

`ssl_verify` disables SSL certificate check.

### timeout

Value in seconds. Default is 10 seconds. `timeout` must be less than 20s.

### headers

Custom headers as key/value to send with the request.

     headers:
        MY-1HEADER: value1
        MY-2HEADER: value2

### asserts

#### assert_status_code_is
Expects the response status code

    assert_status_code_is: 200

#### assert_status_code_is_not
Expects the response status code is not

    assert_status_code_is_not: 500

#### assert_header_is_set
Expects a response header is set

    assert_header_is_set: My-Header

#### assert_header_is_not_set
Expects a response header is not set

    assert_header_is_not_set: My-Header

#### assert_header_value_contains
Expects a response header contains a string in the value

    assert_header_value_contains:
      My-Header: Hello 

#### assert_body_contains
Expects the body contains a string

    assert_body_contains: Hello World

#### assert_is_json
Expects the response is parseable as JSON.

    assert_is_json

#### assert_is_not_json
Expects the response is not parseable as JSON.

    assert_is_not_json
