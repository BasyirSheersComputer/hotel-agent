#!/bin/sh

# Replace placeholder in script.js with environment variable
if [ -n "$BACKEND_URL" ]; then
    echo "Injecting backend URL: $BACKEND_URL"
    # We use sed to replace the placeholder or the hardcoded URL
    # Since we already have a hardcoded URL in script.js, we'll replace the whole assignment line or use a specific marker
    
    # Strategy: Inject a global variable at the top of index.html or script.js
    # Simpler: Replace the specific line in script.js
    
    # Let's look for the line: : (window.API_URL || '...');
    # And replace it with: : '$BACKEND_URL';
    
    sed -i "s|window.API_URL || '.*'|'$BACKEND_URL'|g" /usr/share/nginx/html/script.js
fi

# Continue with default entrypoint behavior (which runs other scripts in /docker-entrypoint.d/)
exit 0
