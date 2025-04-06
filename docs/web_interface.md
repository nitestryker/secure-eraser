# Web Interface

This guide explains how to use the web interface included with Secure Eraser, which provides an interactive, browser-based way to access the tool's functionality.

## Understanding the Web Interface

The web interface is a simplified demonstration of Secure Eraser's capabilities, designed for:

- Visualizing the secure erasure process
- Displaying reports in an interactive format
- Providing a user-friendly way to view available commands
- Demonstrating the tool's functionality

**Note:** The web interface is primarily a demonstration tool. For security-critical or production operations, the command-line interface is recommended.

## Starting the Web Interface

To start the web interface:

```bash
python main.py
```

This launches a Flask web server that's accessible in your browser.

By default, the web interface runs on port 5000. You can access it at:

```
http://localhost:5000
```

## Web Interface Features

### Home Page

The home page provides:

- An overview of Secure Eraser
- Links to available operations
- Information about the latest features
- Security notices and warnings

### Demo Operation

The demo page allows you to run a simple demonstration of the secure erasure process:

1. Navigate to the "Run Demo" page
2. The system will create a temporary file
3. The file will be securely erased using NIST 800-88 Purge standard
4. A detailed HTML report will be generated
5. Both the command output and HTML report will be displayed

This is useful for:
- Understanding the tool's operation
- Seeing the verification process in action
- Exploring the HTML report format
- Testing that the tool is working correctly

### Command Reference

The commands page displays all available commands and options:

1. Navigate to the "View Commands" page
2. A comprehensive list of all commands, options, and examples is displayed
3. You can use this as a reference while learning the tool

This is useful for:
- Learning available options
- Understanding command syntax
- Exploring advanced features
- Finding examples for specific operations

## Web Interface Security Considerations

The web interface is designed for demonstration and local use. Be aware of these security considerations:

1. **Local Use Only**: By default, the interface binds to 0.0.0.0, which allows connections from any network interface. For public-facing servers, use appropriate firewall rules or modify the binding.

2. **No Authentication**: The demo interface has no authentication. Do not expose it on public networks.

3. **Limited Operations**: The web interface only performs operations on temporary files created for demonstration purposes.

4. **Security Warning**: A prominent warning indicates that for security-critical operations, the command-line interface should be used.

## Customizing the Web Interface

The web interface can be customized for specific deployment scenarios:

### Changing the Port

To run the web interface on a different port:

```bash
python main.py --port 8080
```

### Enabling Debug Mode

For development and troubleshooting:

```bash
python main.py --debug
```

### Custom Templates

You can customize the appearance by modifying the HTML templates in the code.

## Extended Web Interface Features

Advanced deployments can enable additional features:

### Custom Demo Operations

Configure specific demonstration scenarios:

```bash
python main.py --demo-scenario military
```

Available scenarios:
- `basic`: Standard erasure demo
- `military`: Military-grade standards demo
- `custom`: Custom pattern demo
- `advanced`: Advanced verification demo

### API Mode

Enable a REST API for automation:

```bash
python main.py --api-mode
```

This allows programmatic access to Secure Eraser functionality.

## Web Interface Architecture

The web interface consists of:

1. **Flask Backend**: Handles HTTP requests and executes Secure Eraser commands
2. **Bootstrap UI**: Provides responsive, mobile-friendly interface
3. **Jinja2 Templates**: Renders HTML output
4. **In-Memory Processing**: Operations are performed on temporary files

## Best Practices

1. **Use for Demonstration Only**: The web interface is not intended for production use
2. **Don't Expose Publicly**: Keep the interface on local or protected networks
3. **Use Command Line for Production**: Use the CLI for security-critical operations
4. **Monitor Resources**: The web server adds overhead to the system

## Troubleshooting

### Web Interface Won't Start

If the web interface fails to start:
- Check if port 5000 is already in use
- Ensure Flask is installed
- Verify you have permission to bind to the port
- Check for errors in the console output

### Demo Operation Fails

If the demo operation fails:
- Check temporary directory permissions
- Verify Secure Eraser is functioning correctly
- Check for sufficient disk space
- Examine error messages in the output

### Browser Issues

If the interface doesn't display correctly:
- Use a modern browser (Chrome, Firefox, Edge, Safari)
- Clear browser cache
- Enable JavaScript
- Disable content blockers that might interfere

## Related Documentation

- [Basic Usage](basic_usage.md) - Command-line usage information
- [Reporting](reporting.md) - Understanding the reports displayed in the interface
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide