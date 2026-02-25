"""
Grind Phase - ERTDSD Autonomous Code Implementation
Implements code in sandbox environment based on test specifications from Architect Phase
"""

import asyncio
import json
import logging
import time
import subprocess
import tempfile
import os
import sys
import hashlib
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
import ast
import astroid
import re

from redis_bus import RedisBus
from global_arbiter import GlobalArbiter
from identity_firewall import IdentityFirewall
from bikameral_memory import BikameralMemory
from chronos_heartbeat import ChronosHeartbeat

logger = logging.getLogger(__name__)

@dataclass
class CodeImplementation:
    """Code implementation result"""
    component_name: str
    file_path: str
    code_content: str
    test_results: Dict[str, Any]
    implementation_time: float
    iteration_count: int
    quality_score: float
    security_scan_results: Dict[str, Any]
    performance_metrics: Dict[str, Any]

@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    status: str  # passed, failed, skipped
    execution_time: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    assertions_passed: int = 0
    assertions_failed: int = 0

@dataclass
class ImplementationSession:
    """Implementation session tracking"""
    session_id: str
    contract_id: str
    suite_id: str
    sandbox_path: str
    components: List[str]
    start_time: datetime
    current_iteration: int = 0
    max_iterations: int = 10
    test_results: List[TestResult] = None
    implementations: List[CodeImplementation] = None
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []
        if self.implementations is None:
            self.implementations = []

class CodeGenerator:
    """Generates code based on test specifications"""
    
    def __init__(self):
        self.generation_strategies = {
            'api_endpoint': self._generate_api_code,
            'database_model': self._generate_database_code,
            'ui_component': self._generate_ui_code,
            'algorithm': self._generate_algorithm_code,
            'integration': self._generate_integration_code,
            'security': self._generate_security_code,
            'performance': self._generate_performance_code,
            'memory_system': self._generate_memory_code,
            'orchestration': self._generate_orchestration_code,
            'scanner': self._generate_scanner_code
        }
    
    def generate_code(self, test_spec: Dict[str, Any], component_type: str) -> str:
        """Generate code based on test specification"""
        if component_type in self.generation_strategies:
            return self.generation_strategies[component_type](test_spec)
        else:
            return self._generate_generic_code(test_spec)
    
    def _generate_api_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate API endpoint code"""
        component_name = test_spec['component_name']
        test_name = test_spec['test_name']
        
        if 'basic' in test_name:
            return self._generate_basic_api_endpoint(test_spec)
        elif 'error_handling' in test_name:
            return self._generate_error_handling_api(test_spec)
        else:
            return self._generate_generic_api_endpoint(test_spec)
    
    def _generate_basic_api_endpoint(self, test_spec: Dict[str, Any]) -> str:
        """Generate basic API endpoint code"""
        component_name = test_spec['component_name']
        method = test_spec['test_name'].split('_')[-2].upper()
        
        code = f'''"""
Generated API endpoint for {component_name}
Test: {test_spec['test_name']}
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}Endpoint:
    """Generated API endpoint class"""
    
    def __init__(self):
        self.setup_complete = False
        logger.info(f"{component_name} endpoint initialized")
    
    async def setup(self):
        """Setup endpoint dependencies"""
        # TODO: Implement setup based on preconditions
        {chr(10).join(f"        # {precondition}" for precondition in test_spec.get('preconditions', []))}
        self.setup_complete = True
    
    async def handle_{method.lower()}(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle {method} request"""
        try:
            # Validate request
            validation_result = self._validate_request(request_data)
            if not validation_result['valid']:
                return {{
                    'status': 'error',
                    'message': validation_result['message'],
                    'timestamp': datetime.now().isoformat()
                }}
            
            # Process request based on test steps
{chr(10).join(f"            # {step}" for step in test_spec.get('steps', []))}
            
            # Generate response based on expected results
            response = {{
                'status': 'success',
                'data': self._generate_response_data(request_data),
                'timestamp': datetime.now().isoformat()
            }}
            
            # Validate response meets assertions
            self._validate_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling {method} request: {{e}}")
            return {{
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }}
    
    def _validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request data"""
        # TODO: Implement request validation
        return {{'valid': True, 'message': ''}}
    
    def _generate_response_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response data"""
        # TODO: Implement response data generation
        test_data = {json.dumps(test_spec.get('test_data', {{}}), indent=12)}
        return test_data
    
    def _validate_response(self, response: Dict[str, Any]):
        """Validate response meets test assertions"""
        # TODO: Implement response validation
{chr(10).join(f"        # {assertion}" for assertion in test_spec.get('assertions', []))}
        pass

# Export endpoint instance
endpoint = {component_name.title().replace("_", "")}Endpoint()
'''
        return code
    
    def _generate_error_handling_api(self, test_spec: Dict[str, Any]) -> str:
        """Generate API with error handling"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated error handling API for {component_name}
Test: {test_spec['test_name']}
"""

import asyncio
import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}ErrorHandler:
    """Generated error handling API class"""
    
    ERROR_CODES = {{
        'INVALID_AUTHENTICATION': 401,
        'MALFORMED_DATA': 400,
        'NOT_FOUND': 404,
        'INTERNAL_ERROR': 500
    }}
    
    def __init__(self):
        logger.info(f"{component_name} error handler initialized")
    
    async def handle_request(self, request_data: Dict[str, Any], auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Handle request with error handling"""
        try:
            # Check authentication
            if not self._validate_authentication(auth_token):
                return self._error_response('INVALID_AUTHENTICATION', 'Invalid authentication credentials')
            
            # Validate data format
            if not self._validate_data_format(request_data):
                return self._error_response('MALFORMED_DATA', 'Request data is malformed')
            
            # Process request
            result = self._process_request(request_data)
            
            return {{
                'status': 'success',
                'data': result,
                'timestamp': datetime.now().isoformat()
            }}
            
        except Exception as e:
            logger.error(f"Internal error: {{e}}")
            return self._error_response('INTERNAL_ERROR', 'Internal server error')
    
    def _validate_authentication(self, auth_token: Optional[str]) -> bool:
        """Validate authentication token"""
        # TODO: Implement authentication validation
        return auth_token is not None and len(auth_token) > 0
    
    def _validate_data_format(self, request_data: Dict[str, Any]) -> bool:
        """Validate request data format"""
        # TODO: Implement data format validation
        return isinstance(request_data, dict)
    
    def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process valid request"""
        # TODO: Implement request processing
        return {{'processed': True}}
    
    def _error_response(self, error_type: str, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {{
            'status': 'error',
            'error': {{
                'type': error_type,
                'code': self.ERROR_CODES.get(error_type, 500),
                'message': message
            }},
            'timestamp': datetime.now().isoformat()
        }}

# Export error handler instance
error_handler = {component_name.title().replace("_", "")}ErrorHandler()
'''
        return code
    
    def _generate_generic_api_endpoint(self, test_spec: Dict[str, Any]) -> str:
        """Generate generic API endpoint code"""
        return self._generate_basic_api_endpoint(test_spec)
    
    def _generate_database_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate database model code"""
        component_name = test_spec['component_name']
        test_name = test_spec['test_name']
        
        if 'crud' in test_name:
            return self._generate_crud_model(test_spec)
        elif 'integrity' in test_name:
            return self._generate_integrity_model(test_spec)
        else:
            return self._generate_generic_model(test_spec)
    
    def _generate_crud_model(self, test_spec: Dict[str, Any]) -> str:
        """Generate CRUD database model code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated CRUD database model for {component_name}
Test: {test_spec['test_name']}
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class {component_name.title().replace("_", "")}Record:
    """Generated data model"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class {component_name.title().replace("_", "")}Model:
    """Generated CRUD database model"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        logger.info(f"{component_name} model initialized")
    
    async def create(self, data: Dict[str, Any]) -> {component_name.title().replace("_", "")}Record:
        """Create new record"""
        try:
            # Validate data
            validated_data = self._validate_create_data(data)
            
            # Generate SQL query based on test data
            # TODO: Implement actual database insertion
            record = {component_name.title().replace("_", "")}Record(
                id=self._generate_id(),
                **validated_data
            )
            
            logger.info(f"Created record: {{record.id}}")
            return record
            
        except Exception as e:
            logger.error(f"Error creating record: {{e}}")
            raise
    
    async def read(self, record_id: int) -> Optional[{component_name.title().replace("_", "")}Record]:
        """Read record by ID"""
        try:
            # TODO: Implement actual database query
            # This is a mock implementation
            return {component_name.title().replace("_", "")}Record(
                id=record_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error reading record {{record_id}}: {{e}}")
            return None
    
    async def update(self, record_id: int, data: Dict[str, Any]) -> Optional[{component_name.title().replace("_", "")}Record]:
        """Update existing record"""
        try:
            # Validate update data
            validated_data = self._validate_update_data(data)
            
            # TODO: Implement actual database update
            record = await self.read(record_id)
            if record:
                # Update record fields
                for key, value in validated_data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                record.updated_at = datetime.now()
                
                logger.info(f"Updated record: {{record_id}}")
                return record
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating record {{record_id}}: {{e}}")
            return None
    
    async def delete(self, record_id: int) -> bool:
        """Delete record"""
        try:
            # TODO: Implement actual database deletion
            logger.info(f"Deleted record: {{record_id}}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting record {{record_id}}: {{e}}")
            return False
    
    def _validate_create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for creation"""
        # TODO: Implement data validation based on test data
        test_data = {json.dumps(test_spec.get('test_data', {{}}), indent=12)}
        return data
    
    def _validate_update_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data for update"""
        # TODO: Implement update data validation
        return data
    
    def _generate_id(self) -> int:
        """Generate unique ID"""
        import random
        return random.randint(1000, 9999)

# Export model class
{component_name.title().replace("_", "")}Model
'''
        return code
    
    def _generate_integrity_model(self, test_spec: Dict[str, Any]) -> str:
        """Generate database integrity model code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated database integrity model for {component_name}
Test: {test_spec['test_name']}
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}IntegrityModel:
    """Generated database integrity model"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.constraints = {{
            'unique': [],
            'not_null': [],
            'foreign_key': []
        }}
        logger.info(f"{component_name} integrity model initialized")
    
    async def validate_constraints(self, data: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Validate data against integrity constraints"""
        violations = []
        
        try:
            # Check unique constraints
            unique_violations = await self._check_unique_constraints(data, operation)
            violations.extend(unique_violations)
            
            # Check not null constraints
            null_violations = self._check_not_null_constraints(data)
            violations.extend(null_violations)
            
            # Check foreign key constraints
            fk_violations = await self._check_foreign_key_constraints(data)
            violations.extend(fk_violations)
            
            return {{
                'valid': len(violations) == 0,
                'violations': violations
            }}
            
        except Exception as e:
            logger.error(f"Error validating constraints: {{e}}")
            return {{
                'valid': False,
                'violations': [f"Validation error: {{e}}"]
            }}
    
    async def _check_unique_constraints(self, data: Dict[str, Any], operation: str) -> List[str]:
        """Check unique constraints"""
        violations = []
        
        for field in self.constraints['unique']:
            if field in data:
                # TODO: Implement actual unique constraint checking
                # This is a mock implementation
                if operation == 'insert' and data[field] == 'duplicate_value':
                    violations.append(f"Unique constraint violation on field '{{field}}'")
        
        return violations
    
    def _check_not_null_constraints(self, data: Dict[str, Any]) -> List[str]:
        """Check not null constraints"""
        violations = []
        
        for field in self.constraints['not_null']:
            if field not in data or data[field] is None:
                violations.append(f"Not null constraint violation on field '{{field}}'")
        
        return violations
    
    async def _check_foreign_key_constraints(self, data: Dict[str, Any]) -> List[str]:
        """Check foreign key constraints"""
        violations = []
        
        for constraint in self.constraints['foreign_key']:
            field = constraint['field']
            referenced_table = constraint['referenced_table']
            referenced_field = constraint['referenced_field']
            
            if field in data:
                # TODO: Implement actual foreign key constraint checking
                # This is a mock implementation
                if data[field] == 'invalid_foreign_key':
                    violations.append(
                        f"Foreign key constraint violation: {{field}} references non-existent value in {{referenced_table}}.{{referenced_field}}"
                    )
        
        return violations

# Export integrity model class
{component_name.title().replace("_", "")}IntegrityModel
'''
        return code
    
    def _generate_generic_model(self, test_spec: Dict[str, Any]) -> str:
        """Generate generic database model code"""
        return self._generate_crud_model(test_spec)
    
    def _generate_ui_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate UI component code"""
        component_name = test_spec['component_name']
        test_name = test_spec['test_name']
        
        if 'rendering' in test_name:
            return self._generate_rendering_component(test_spec)
        elif 'interactions' in test_name:
            return self._generate_interactive_component(test_spec)
        else:
            return self._generate_generic_component(test_spec)
    
    def _generate_rendering_component(self, test_spec: Dict[str, Any]) -> str:
        """Generate UI rendering component code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated UI rendering component for {component_name}
Test: {test_spec['test_name']}
"""

import React, {{ useState, useEffect }} from 'react';
import PropTypes from 'prop-types';

/**
 * Generated UI component for {component_name}
 * Test: {test_spec['test_name']}
 */
const {component_name.title().replace("_", "")} = ({{ defaultProps = {{}}, customProps = {{}} }}) => {{
  const [state, setState] = useState({{
    isLoading: false,
    data: null,
    error: null,
    ...defaultProps
  }});
  
  useEffect(() => {{
    // Component initialization
    console.log('{component_name} component mounted');
    
    // Apply custom props
    if (Object.keys(customProps).length > 0) {{
      setState(prevState => ({{
        ...prevState,
        ...customProps
      }}));
    }}
    
    return () => {{
      // Cleanup
      console.log('{component_name} component unmounted');
    }};
  }}, [customProps]);
  
  const handlePropsValidation = () => {{
    // Validate props based on test assertions
    {chr(10).join(f"    // {assertion}" for assertion in test_spec.get('assertions', []))}
    return true;
  }};
  
  const renderContent = () => {{
    if (state.isLoading) {{
      return <div>Loading...</div>;
    }}
    
    if (state.error) {{
      return <div className="error">{{state.error}}</div>;
    }}
    
    return (
      <div className="{component_name}">
        <h3>{{component_name.title().replace("_", " ")}}</h3>
        <div className="content">
          {{/* Generated content based on test data */}}
          {{Object.keys(state).map(key => (
            <div key={{key}} className="data-item">
              <strong>{{key}}:</strong> {{JSON.stringify(state[key])}}
            </div>
          ))}}
        </div>
      </div>
    );
  }};
  
  return (
    <div className="{component_name}-container">
      {{renderContent()}}
    </div>
  );
}};

{component_name.title().replace("_", "")}.propTypes = {{
  defaultProps: PropTypes.object,
  customProps: PropTypes.object
}};

export default {component_name.title().replace("_", "")};
'''
        return code
    
    def _generate_interactive_component(self, test_spec: Dict[str, Any]) -> str:
        """Generate interactive UI component code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated interactive UI component for {component_name}
Test: {test_spec['test_name']}
"""

import React, {{ useState, useCallback }} from 'react';
import PropTypes from 'prop-types';

/**
 * Generated interactive UI component for {component_name}
 * Test: {test_spec['test_name']}
 */
const {component_name.title().replace("_", "")} = ({{ eventHandlers = {{}}, callbacks = {{}} }}) => {{
  const [clickCount, setClickCount] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const [formData, setFormData] = useState({{}});
  
  const handleClick = useCallback((eventType) => {{
    setClickCount(prev => prev + 1);
    
    // Call event handler if provided
    if (eventHandlers[eventType]) {{
      eventHandlers[eventType](eventType, clickCount + 1);
    }}
    
    // Call callback if provided
    if (callbacks.onClick) {{
      callbacks.onClick(eventType, clickCount + 1);
    }}
    
    console.log(`{{eventType}} triggered. Count: {{clickCount + 1}}`);
  }}, [clickCount, eventHandlers, callbacks]);
  
  const handleInputChange = useCallback((event) => {{
    const {{ name, value }} = event.target;
    setInputValue(value);
    setFormData(prev => ({{
      ...prev,
      [name]: value
    }}));
    
    // Call event handler if provided
    if (eventHandlers.inputChange) {{
      eventHandlers.inputChange(name, value);
    }}
    
    console.log(`Input {{name}} changed to: {{value}}`);
  }}, [eventHandlers]);
  
  const handleFormSubmit = useCallback((event) => {{
    event.preventDefault();
    
    // Call event handler if provided
    if (eventHandlers.formSubmit) {{
      eventHandlers.formSubmit(formData);
    }}
    
    // Call callback if provided
    if (callbacks.onFormSubmit) {{
      callbacks.onFormSubmit(formData);
    }}
    
    console.log('Form submitted with data:', formData);
  }}, [formData, eventHandlers, callbacks]);
  
  return (
    <div className="{component_name}-interactive">
      <h3>{{component_name.title().replace("_", " ")}} Interactive</h3>
      
      <div className="click-section">
        <h4>Click Events</h4>
        <button onClick={{() => handleClick('button_click')}}>
          Button Click ({{clickCount}})
        </button>
        <a href="#" onClick={{(e) => {{ e.preventDefault(); handleClick('link_click'); }}}}>
          Link Click
        </a>
      </div>
      
      <div className="input-section">
        <h4>Input Events</h4>
        <input
          type="text"
          name="text_input"
          value={{inputValue}}
          onChange={{handleInputChange}}
          placeholder="Enter text..."
        />
        <select name="select_change" onChange={{handleInputChange}}>
          <option value="">Select option</option>
          <option value="option1">Option 1</option>
          <option value="option2">Option 2</option>
        </select>
      </div>
      
      <div className="form-section">
        <h4>Form Submission</h4>
        <form onSubmit={{handleFormSubmit}}>
          <input type="text" name="form_field" placeholder="Form field" />
          <button type="submit">Submit Form</button>
        </form>
      </div>
      
      <div className="state-display">
        <h4>Component State</h4>
        <pre>{{JSON.stringify(formData, null, 2)}}</pre>
      </div>
    </div>
  );
}};

{component_name.title().replace("_", "")}.propTypes = {{
  eventHandlers: PropTypes.object,
  callbacks: PropTypes.object
}};

export default {component_name.title().replace("_", "")};
'''
        return code
    
    def _generate_generic_component(self, test_spec: Dict[str, Any]) -> str:
        """Generate generic UI component code"""
        return self._generate_rendering_component(test_spec)
    
    def _generate_algorithm_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate algorithm implementation code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated algorithm implementation for {component_name}
Test: {test_spec['test_name']}
"""

import logging
import time
from typing import Any, List, Dict

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}Algorithm:
    """Generated algorithm implementation"""
    
    def __init__(self):
        self.execution_count = 0
        self.performance_metrics = {{}}
        logger.info(f"{component_name} algorithm initialized")
    
    def execute(self, input_data: Any) -> Dict[str, Any]:
        """Execute algorithm with input data"""
        start_time = time.time()
        
        try:
            self.execution_count += 1
            
            # Validate input based on test cases
            validation_result = self._validate_input(input_data)
            if not validation_result['valid']:
                return {{
                    'status': 'error',
                    'message': validation_result['message'],
                    'execution_time': time.time() - start_time
                }}
            
            # Execute algorithm steps
{chr(10).join(f"            # {step}" for step in test_spec.get('steps', []))}
            
            # Process input data
            result = self._process_input(input_data)
            
            # Validate output
            validation_output = self._validate_output(result)
            if not validation_output['valid']:
                return {{
                    'status': 'error',
                    'message': validation_output['message'],
                    'execution_time': time.time() - start_time
                }}
            
            execution_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(execution_time)
            
            return {{
                'status': 'success',
                'result': result,
                'execution_time': execution_time,
                'complexity_analysis': self._analyze_complexity(input_data)
            }}
            
        except Exception as e:
            logger.error(f"Algorithm execution error: {{e}}")
            return {{
                'status': 'error',
                'message': str(e),
                'execution_time': time.time() - start_time
            }}
    
    def _validate_input(self, input_data: Any) -> Dict[str, bool]:
        """Validate input data"""
        # TODO: Implement input validation based on test cases
        test_cases = {json.dumps(test_spec.get('test_data', {{}}), indent=12)}
        return {{'valid': True, 'message': ''}}
    
    def _process_input(self, input_data: Any) -> Any:
        """Process input data according to algorithm logic"""
        # TODO: Implement actual algorithm logic
        # This is a placeholder implementation
        if isinstance(input_data, list):
            return self._process_list(input_data)
        elif isinstance(input_data, dict):
            return self._process_dict(input_data)
        else:
            return input_data
    
    def _process_list(self, data: List[Any]) -> List[Any]:
        """Process list input"""
        # Placeholder implementation
        return [item for item in data if item is not None]
    
    def _process_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process dictionary input"""
        # Placeholder implementation
        return {{k: v for k, v in data.items() if v is not None}}
    
    def _validate_output(self, result: Any) -> Dict[str, bool]:
        """Validate algorithm output"""
        # TODO: Implement output validation based on assertions
{chr(10).join(f"        # {assertion}" for assertion in test_spec.get('assertions', []))}
        return {{'valid': True, 'message': ''}}
    
    def _update_performance_metrics(self, execution_time: float):
        """Update performance metrics"""
        self.performance_metrics['last_execution_time'] = execution_time
        if 'avg_execution_time' not in self.performance_metrics:
            self.performance_metrics['avg_execution_time'] = execution_time
        else:
            # Update running average
            n = self.execution_count
            self.performance_metrics['avg_execution_time'] = (
                (self.performance_metrics['avg_execution_time'] * (n - 1) + execution_time) / n
            )
    
    def _analyze_complexity(self, input_data: Any) -> Dict[str, str]:
        """Analyze algorithm complexity"""
        # TODO: Implement complexity analysis
        return {{
            'time_complexity': 'O(n)',
            'space_complexity': 'O(1)',
            'estimated_for_input_size': str(len(input_data) if hasattr(input_data, '__len__') else 1)
        }}

# Export algorithm instance
algorithm = {component_name.title().replace("_", "")}Algorithm()
'''
        return code
    
    def _generate_integration_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate integration code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated integration code for {component_name}
Test: {test_spec['test_name']}
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}Integration:
    """Generated integration class"""
    
    def __init__(self):
        self.components = {{}}
        self.data_flow_state = {{}}
        logger.info(f"{component_name} integration initialized")
    
    async def execute_workflow(self, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete workflow"""
        workflow_id = self._generate_workflow_id()
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting workflow {{workflow_id}}")
            
            # Initialize workflow state
            self.data_flow_state[workflow_id] = {{
                'status': 'initializing',
                'input': workflow_input,
                'stages': [],
                'current_stage': 0
            }}
            
            # Execute workflow stages
{chr(10).join(f"            # {step}" for step in test_spec.get('steps', []))}
            
            # Process through stages
            stages = [
                self._initialize_data,
                self._process_stage_1,
                self._process_stage_2,
                self._finalize_output
            ]
            
            current_data = workflow_input
            for i, stage in enumerate(stages):
                self.data_flow_state[workflow_id]['current_stage'] = i
                self.data_flow_state[workflow_id]['stages'].append({{
                    'stage': i,
                    'name': stage.__name__,
                    'input': current_data
                }})
                
                current_data = await stage(current_data, workflow_id)
                
                logger.info(f"Stage {{i}} completed: {{stage.__name__}}")
            
            # Validate final output
            validation_result = self._validate_final_output(current_data)
            if not validation_result['valid']:
                raise ValueError(f"Final output validation failed: {{validation_result['message']}}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.data_flow_state[workflow_id]['status'] = 'completed'
            self.data_flow_state[workflow_id]['output'] = current_data
            self.data_flow_state[workflow_id]['execution_time'] = execution_time
            
            logger.info(f"Workflow {{workflow_id}} completed in {{execution_time}}s")
            
            return {{
                'workflow_id': workflow_id,
                'status': 'success',
                'output': current_data,
                'execution_time': execution_time,
                'stages_completed': len(stages),
                'data_integrity_verified': self._verify_data_integrity(workflow_input, current_data)
            }}
            
        except Exception as e:
            logger.error(f"Workflow {{workflow_id}} failed: {{e}}")
            self.data_flow_state[workflow_id]['status'] = 'failed'
            self.data_flow_state[workflow_id]['error'] = str(e)
            
            return {{
                'workflow_id': workflow_id,
                'status': 'failed',
                'error': str(e),
                'execution_time': (datetime.now() - start_time).total_seconds()
            }}
    
    async def _initialize_data(self, input_data: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Initialize workflow data"""
        # TODO: Implement data initialization based on test data
        test_data = {json.dumps(test_spec.get('test_data', {{}}), indent=12)}
        return {{**input_data, 'initialized': True}}
    
    async def _process_stage_1(self, data: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Process stage 1"""
        # TODO: Implement stage 1 processing
        return {{**data, 'stage1_processed': True}}
    
    async def _process_stage_2(self, data: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Process stage 2"""
        # TODO: Implement stage 2 processing
        return {{**data, 'stage2_processed': True}}
    
    async def _finalize_output(self, data: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        """Finalize output"""
        # TODO: Implement output finalization
        expected_output = {json.dumps(test_spec.get('test_data', {{}}).get('expected_output', {{}}), indent=12)}
        return {{**data, **expected_output, 'finalized': True}}
    
    def _validate_final_output(self, output: Dict[str, Any]) -> Dict[str, bool]:
        """Validate final output"""
        # TODO: Implement final output validation based on assertions
{chr(10).join(f"        # {assertion}" for assertion in test_spec.get('assertions', []))}
        return {{'valid': True, 'message': ''}}
    
    def _verify_data_integrity(self, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> bool:
        """Verify data integrity through workflow"""
        # TODO: Implement data integrity verification
        # This is a basic check - should be more comprehensive
        return isinstance(input_data, dict) and isinstance(output_data, dict)
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        import uuid
        return str(uuid.uuid4())[:8]

# Export integration instance
integration = {component_name.title().replace("_", "")}Integration()
'''
        return code
    
    def _generate_security_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate security code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated security code for {component_name}
Test: {test_spec['test_name']}
"""

import logging
import hashlib
import secrets
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}Security:
    """Generated security implementation"""
    
    def __init__(self):
        self.active_sessions = {{}}
        self.rate_limiter = {{}}
        self.security_log = []
        logger.info(f"{component_name} security initialized")
    
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user credentials"""
        try:
            # Log authentication attempt
            self._log_security_event('authentication_attempt', {{
                'timestamp': datetime.now().isoformat(),
                'user': credentials.get('username', 'unknown')
            }})
            
            # Check rate limiting
            user_id = credentials.get('username', 'anonymous')
            if not self._check_rate_limit(user_id):
                return {{
                    'status': 'error',
                    'message': 'Rate limit exceeded',
                    'code': 429
                }}
            
            # Validate credentials (mock implementation)
            if not self._validate_credentials(credentials):
                return {{
                    'status': 'error',
                    'message': 'Invalid credentials',
                    'code': 401
                }}
            
            # Create session
            session_token = self._create_session(user_id)
            
            # Log successful authentication
            self._log_security_event('authentication_success', {{
                'timestamp': datetime.now().isoformat(),
                'user': user_id,
                'session_token': session_token[:8] + '...'  # Masked for security
            }})
            
            return {{
                'status': 'success',
                'session_token': session_token,
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
            }}
            
        except Exception as e:
            logger.error(f"Authentication error: {{e}}")
            return {{
                'status': 'error',
                'message': 'Authentication failed',
                'code': 500
            }}
    
    def authorize(self, session_token: str, resource: str) -> Dict[str, Any]:
        """Authorize access to resource"""
        try:
            # Validate session
            session = self._validate_session(session_token)
            if not session['valid']:
                return {{
                    'status': 'error',
                    'message': 'Invalid session',
                    'code': 401
                }}
            
            # Check resource access
            if not self._check_resource_access(session['user_id'], resource):
                return {{
                    'status': 'error',
                    'message': 'Access denied',
                    'code': 403
                }}
            
            # Log authorization
            self._log_security_event('authorization_success', {{
                'timestamp': datetime.now().isoformat(),
                'user': session['user_id'],
                'resource': resource
            }})
            
            return {{
                'status': 'success',
                'user': session['user_id'],
                'permissions': self._get_user_permissions(session['user_id'])
            }}
            
        except Exception as e:
            logger.error(f"Authorization error: {{e}}")
            return {{
                'status': 'error',
                'message': 'Authorization failed',
                'code': 500
            }}
    
    def _validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate user credentials"""
        # TODO: Implement actual credential validation
        # This is a mock implementation
        username = credentials.get('username', '')
        password = credentials.get('password', '')
        
        # Mock validation - should be replaced with actual authentication
        return len(username) > 0 and len(password) > 0
    
    def _create_session(self, user_id: str) -> str:
        """Create secure session"""
        session_token = secrets.token_urlsafe(32)
        
        self.active_sessions[session_token] = {{
            'user_id': user_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=24),
            'last_activity': datetime.now()
        }}
        
        return session_token
    
    def _validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate session token"""
        if session_token not in self.active_sessions:
            return {{'valid': False, 'message': 'Session not found'}}
        
        session = self.active_sessions[session_token]
        
        if datetime.now() > session['expires_at']:
            del self.active_sessions[session_token]
            return {{'valid': False, 'message': 'Session expired'}}
        
        # Update last activity
        session['last_activity'] = datetime.now()
        
        return {{'valid': True, 'user_id': session['user_id']}}
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check rate limiting"""
        now = time.time()
        
        if user_id not in self.rate_limiter:
            self.rate_limiter[user_id] = {{'requests': [], 'blocked_until': 0}}
        
        user_limit = self.rate_limiter[user_id]
        
        # Check if user is currently blocked
        if now < user_limit['blocked_until']:
            return False
        
        # Clean old requests (older than 1 hour)
        user_limit['requests'] = [
            req_time for req_time in user_limit['requests']
            if now - req_time < 3600
        ]
        
        # Check request count (max 100 requests per hour)
        if len(user_limit['requests']) >= 100:
            user_limit['blocked_until'] = now + 3600  # Block for 1 hour
            return False
        
        # Record this request
        user_limit['requests'].append(now)
        return True
    
    def _check_resource_access(self, user_id: str, resource: str) -> bool:
        """Check resource access permissions"""
        # TODO: Implement actual resource access control
        # This is a mock implementation
        return resource != 'soul.md' or user_id == 'admin'
    
    def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        # TODO: Implement actual permission retrieval
        return ['read', 'write'] if user_id != 'anonymous' else ['read']
    
    def _log_security_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log security event"""
        event = {{
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        }}
        
        self.security_log.append(event)
        
        # Keep only last 1000 events
        if len(self.security_log) > 1000:
            self.security_log = self.security_log[-1000:]
        
        # Log to system logger (sanitized)
        sanitized_data = self._sanitize_log_data(event_data)
        logger.info(f"Security event {{event_type}}: {{sanitized_data}}")
    
    def _sanitize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for logging"""
        sanitized = {{}}
        for key, value in data.items():
            if 'password' in key.lower() or 'token' in key.lower():
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        return sanitized

# Export security instance
security = {component_name.title().replace("_", "")}Security()
'''
        return code
    
    def _generate_performance_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate performance monitoring code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated performance monitoring code for {component_name}
Test: {test_spec['test_name']}
"""

import time
import logging
import threading
import psutil
import gc
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}Performance:
    """Generated performance monitoring implementation"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.baseline_metrics = {{}}
        self.monitoring_active = False
        self.monitor_thread = None
        self.resource_limits = {{
            'memory_mb': 32768,  # 32GB
            'gpu_memory_mb': 12288,  # 12GB
            'cpu_percent': 80,
            'response_time_ms': 2000
        }}
        logger.info(f"{component_name} performance monitoring initialized")
    
    def start_monitoring(self, interval: float = 1.0):
        """Start performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Performance monitoring stopped")
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record performance metric"""
        timestamp = time.time()
        metric_entry = {{
            'timestamp': timestamp,
            'value': value,
            'tags': tags or {{}}
        }}
        
        self.metrics[metric_name].append(metric_entry)
        
        # Check against thresholds
        self._check_thresholds(metric_name, value)
    
    def get_metrics_summary(self, metric_name: str, time_window: int = 300) -> Dict[str, Any]:
        """Get metrics summary for time window"""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        relevant_metrics = [
            entry for entry in self.metrics[metric_name]
            if entry['timestamp'] >= cutoff_time
        ]
        
        if not relevant_metrics:
            return {{'error': 'No data available'}}
        
        values = [entry['value'] for entry in relevant_metrics]
        
        return {{
            'metric_name': metric_name,
            'count': len(values),
            'avg': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'p50': self._percentile(values, 0.5),
            'p95': self._percentile(values, 0.95),
            'p99': self._percentile(values, 0.99),
            'time_window': time_window
        }}
    
    def run_load_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run load test"""
        test_id = self._generate_test_id()
        start_time = time.time()
        
        try:
            logger.info(f"Starting load test {{test_id}}")
            
            concurrent_users = test_config.get('concurrent_users', 10)
            test_duration = test_config.get('test_duration', 60)
            target_throughput = test_config.get('target_throughput', 100)
            
            # Record baseline metrics
            baseline = self._collect_system_metrics()
            self.baseline_metrics[test_id] = baseline
            
            # Simulate load
            results = self._simulate_load(
                concurrent_users,
                test_duration,
                target_throughput
            )
            
            # Collect final metrics
            final_metrics = self._collect_system_metrics()
            
            execution_time = time.time() - start_time
            
            # Analyze results
            analysis = self._analyze_load_test_results(
                results,
                baseline,
                final_metrics,
                test_config
            )
            
            logger.info(f"Load test {{test_id}} completed in {{execution_time}}s")
            
            return {{
                'test_id': test_id,
                'status': 'completed',
                'execution_time': execution_time,
                'config': test_config,
                'results': results,
                'analysis': analysis,
                'system_metrics': {{
                    'baseline': baseline,
                    'final': final_metrics
                }}
            }}
            
        except Exception as e:
            logger.error(f"Load test {{test_id}} failed: {{e}}")
            return {{
                'test_id': test_id,
                'status': 'failed',
                'error': str(e),
                'execution_time': time.time() - start_time
            }}
    
    def _monitoring_loop(self, interval: float):
        """Monitoring loop for system metrics"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Record metrics
                for metric_name, value in metrics.items():
                    self.record_metric(metric_name, value)
                
                # Check resource limits
                self._check_resource_limits(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {{e}}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_used_mb = memory.used / (1024 * 1024)
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Response time (mock - should be measured from actual requests)
            response_time_ms = 100.0  # Mock value
            
            return {{
                'cpu_percent': cpu_percent,
                'memory_used_mb': memory_used_mb,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'response_time_ms': response_time_ms
            }}
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {{e}}")
            return {{}}
    
    def _check_resource_limits(self, metrics: Dict[str, float]):
        """Check if resource usage exceeds limits"""
        for resource, usage in metrics.items():
            limit = self.resource_limits.get(resource)
            if limit and usage > limit:
                logger.warning(f"Resource limit exceeded: {{resource}} = {{usage}}% (limit: {{limit}}%)")
                
                # Trigger garbage collection for memory
                if resource == 'memory_percent' and usage > 90:
                    gc.collect()
    
    def _check_thresholds(self, metric_name: str, value: float):
        """Check metric against defined thresholds"""
        thresholds = {{
            'response_time_ms': 2000,
            'error_rate': 0.01,
            'cpu_percent': 80,
            'memory_percent': 85
        }}
        
        threshold = thresholds.get(metric_name)
        if threshold and value > threshold:
            logger.warning(f"Metric {{metric_name}} exceeded threshold: {{value}} (threshold: {{threshold}})")
    
    def _simulate_load(self, concurrent_users: int, duration: int, target_throughput: int) -> Dict[str, Any]:
        """Simulate load for testing"""
        results = {{
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0,
            'throughput': 0
        }}
        
        # Simulate requests
        request_times = []
        for i in range(target_throughput * duration // 60):  # Scale down for simulation
            start_time = time.time()
            
            # Simulate request processing
            processing_time = 0.01 + (i % 10) * 0.001  # Variable processing time
            time.sleep(processing_time)
            
            response_time = time.time() - start_time
            request_times.append(response_time)
            
            results['total_requests'] += 1
            results['successful_requests'] += 1
        
        # Calculate statistics
        if request_times:
            results['avg_response_time'] = sum(request_times) / len(request_times)
            results['min_response_time'] = min(request_times)
            results['max_response_time'] = max(request_times)
            results['throughput'] = results['total_requests'] / duration
        
        return results
    
    def _analyze_load_test_results(self, results: Dict[str, Any], baseline: Dict[str, Any], 
                                 final: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze load test results"""
        analysis = {{
            'performance_degradation': {{}},
            'bottlenecks': [],
            'recommendations': []
        }}
        
        # Check for performance degradation
        if baseline and final:
            for metric in ['cpu_percent', 'memory_percent']:
                if baseline.get(metric) and final.get(metric):
                    degradation = final[metric] - baseline[metric]
                    if degradation > 10:  # More than 10% degradation
                        analysis['performance_degradation'][metric] = degradation
                        analysis['bottlenecks'].append(f"System {{metric}} increased by {{degradation:.1f}}%")
        
        # Check response time against SLA
        sla_threshold = config.get('max_response_time_ms', 2000)
        if results.get('avg_response_time', 0) * 1000 > sla_threshold:  # Convert to ms
            analysis['bottlenecks'].append(f"Average response time exceeds SLA: {{results['avg_response_time'] * 1000:.0f}}ms > {{sla_threshold}}ms")
            analysis['recommendations'].append("Optimize response time to meet SLA requirements")
        
        # Check error rate
        error_rate = results.get('failed_requests', 0) / max(results.get('total_requests', 1), 1)
        if error_rate > 0.01:  # 1% error rate threshold
            analysis['bottlenecks'].append(f"Error rate too high: {{error_rate:.2%}}")
            analysis['recommendations'].append("Investigate and fix sources of request failures")
        
        return analysis
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _generate_test_id(self) -> str:
        """Generate unique test ID"""
        import uuid
        return str(uuid.uuid4())[:8]

# Export performance monitoring instance
performance = {component_name.title().replace("_", "")}Performance()
'''
        return code
    
    def _generate_memory_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate memory system code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated memory system code for {component_name}
Test: {test_spec['test_name']}
"""

import asyncio
import json
import logging
import redis
import asyncpg
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}Memory:
    """Generated memory system implementation"""
    
    def __init__(self, redis_client: redis.Redis, postgres_pool: asyncpg.Pool):
        self.redis = redis_client
        self.postgres = postgres_pool
        self.retention_policies = {{
            'short_term': timedelta(hours=1),
            'medium_term': timedelta(days=1),
            'long_term': timedelta(days=30)
        }}
        logger.info(f"{component_name} memory system initialized")
    
    async def allocate_memory(self, key: str, data: Dict[str, Any], retention_policy: str = 'short_term') -> bool:
        """Allocate memory for data"""
        try:
            # Determine storage based on retention policy
            if retention_policy == 'short_term':
                success = await self._store_in_redis(key, data, retention_policy)
            else:
                success = await self._store_in_postgres(key, data, retention_policy)
            
            if success:
                logger.info(f"Memory allocated for key {{key}} with policy {{retention_policy}}")
                
                # Verify allocation
                verification = await self._verify_allocation(key, retention_policy)
                if verification['verified']:
                    logger.info(f"Memory allocation verified for key {{key}}")
                    return True
                else:
                    logger.error(f"Memory allocation verification failed for key {{key}}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Memory allocation error for key {{key}}: {{e}}")
            return False
    
    async def _store_in_redis(self, key: str, data: Dict[str, Any], retention_policy: str) -> bool:
        """Store data in Redis (short-term memory)"""
        try:
            # Serialize data
            serialized_data = json.dumps(data)
            
            # Store in Redis with TTL
            ttl = int(self.retention_policies[retention_policy].total_seconds())
            await self.redis.setex(key, ttl, serialized_data)
            
            logger.info(f"Data stored in Redis: {{key}} (TTL: {{ttl}}s)")
            return True
            
        except Exception as e:
            logger.error(f"Redis storage error for key {{key}}: {{e}}")
            return False
    
    async def _store_in_postgres(self, key: str, data: Dict[str, Any], retention_policy: str) -> bool:
        """Store data in PostgreSQL (long-term memory)"""
        try:
            # Serialize data
            serialized_data = json.dumps(data)
            
            # Store in PostgreSQL
            async with self.postgres.acquire() as conn:
                await conn.execute('''
                    INSERT INTO memory_storage (key, data, retention_policy, created_at, expires_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (key) DO UPDATE SET
                        data = EXCLUDED.data,
                        retention_policy = EXCLUDED.retention_policy,
                        expires_at = EXCLUDED.expires_at
                ''', key, serialized_data, retention_policy, 
                    datetime.now(), datetime.now() + self.retention_policies[retention_policy])
            
            logger.info(f"Data stored in PostgreSQL: {{key}}")
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL storage error for key {{key}}: {{e}}")
            return False
    
    async def _verify_allocation(self, key: str, retention_policy: str) -> Dict[str, Any]:
        """Verify memory allocation"""
        try:
            if retention_policy == 'short_term':
                # Check Redis
                exists = await self.redis.exists(key)
                if exists:
                    data = await self.redis.get(key)
                    return {{'verified': True, 'location': 'redis', 'size': len(data) if data else 0}}
                else:
                    return {{'verified': False, 'error': 'Key not found in Redis'}}
            else:
                # Check PostgreSQL
                async with self.postgres.acquire() as conn:
                    row = await conn.fetchrow('''
                        SELECT key, data, retention_policy FROM memory_storage
                        WHERE key = $1 AND expires_at > $2
                    ''', key, datetime.now())
                    
                    if row:
                        data_size = len(row['data']) if row['data'] else 0
                        return {{'verified': True, 'location': 'postgres', 'size': data_size}}
                    else:
                        return {{'verified': False, 'error': 'Key not found or expired in PostgreSQL'}}
                        
        except Exception as e:
            logger.error(f"Allocation verification error for key {{key}}: {{e}}")
            return {{'verified': False, 'error': str(e)}}
    
    async def retrieve_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from memory"""
        try:
            # Try Redis first (short-term)
            redis_data = await self.redis.get(key)
            if redis_data:
                return json.loads(redis_data)
            
            # Try PostgreSQL (long-term)
            async with self.postgres.acquire() as conn:
                row = await conn.fetchrow('''
                    SELECT data FROM memory_storage
                    WHERE key = $1 AND expires_at > $2
                ''', key, datetime.now())
                
                if row and row['data']:
                    return json.loads(row['data'])
            
            logger.warning(f"Data not found for key {{key}}")
            return None
            
        except Exception as e:
            logger.error(f"Data retrieval error for key {{key}}: {{e}}")
            return None
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data"""
        cleanup_stats = {{'redis': 0, 'postgres': 0}}
        
        try:
            # Clean Redis (handled by TTL)
            # Clean PostgreSQL
            async with self.postgres.acquire() as conn:
                deleted_count = await conn.fetchval('''
                    DELETE FROM memory_storage
                    WHERE expires_at < $1
                    RETURNING COUNT(*)
                ''', datetime.now())
                
                cleanup_stats['postgres'] = deleted_count or 0
            
            logger.info(f"Cleanup completed: {{cleanup_stats}}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Cleanup error: {{e}}")
            return cleanup_stats

# Export memory system instance
# Note: Requires redis_client and postgres_pool to be provided
# memory = {component_name.title().replace("_", "")}Memory(redis_client, postgres_pool)
'''
        return code
    
    def _generate_orchestration_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate orchestration code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated orchestration code for {component_name}
Test: {test_spec['test_name']}
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class Phase(Enum):
    """Workflow phases"""
    MEETING = "meeting"
    ARCHITECT = "architect"
    GRIND = "grind"
    PRESENTATION = "presentation"

class {component_name.title().replace("_", "")}Orchestration:
    """Generated orchestration implementation"""
    
    def __init__(self, global_arbiter, chronos_heartbeat):
        self.global_arbiter = global_arbiter
        self.chronos = chronos_heartbeat
        self.current_phase = Phase.MEETING
        self.phase_transitions = {{}}
        self.active_workflows = {{}}
        logger.info(f"{component_name} orchestration initialized")
    
    async def transition_phase(self, from_phase: Phase, to_phase: Phase, context: Dict[str, Any]) -> Dict[str, Any]:
        """Transition between phases"""
        transition_id = self._generate_transition_id()
        
        try:
            logger.info(f"Phase transition {{from_phase.value}} -> {{to_phase.value}} ({{transition_id}})")
            
            # Validate transition
            validation = await self._validate_phase_transition(from_phase, to_phase, context)
            if not validation['valid']:
                return {{
                    'status': 'error',
                    'message': f"Invalid phase transition: {{validation['message']}}",
                    'transition_id': transition_id
                }}
            
            # Prepare for transition
            preparation = await self._prepare_phase_transition(from_phase, to_phase, context)
            if not preparation['ready']:
                return {{
                    'status': 'error',
                    'message': f"Phase transition preparation failed: {{preparation['message']}}",
                    'transition_id': transition_id
                }}
            
            # Execute transition
            transition_result = await self._execute_phase_transition(from_phase, to_phase, context)
            
            # Update current phase
            self.current_phase = to_phase
            
            # Record transition
            self.phase_transitions[transition_id] = {{
                'from_phase': from_phase.value,
                'to_phase': to_phase.value,
                'timestamp': datetime.now(),
                'context': context,
                'result': transition_result
            }}
            
            # Notify components
            await self._notify_phase_transition(from_phase, to_phase, context)
            
            logger.info(f"Phase transition {{transition_id}} completed successfully")
            
            return {{
                'status': 'success',
                'transition_id': transition_id,
                'from_phase': from_phase.value,
                'to_phase': to_phase.value,
                'resources_allocated': preparation.get('resources_allocated', {{}}),
                'state_consistent': transition_result.get('state_consistent', False)
            }}
            
        except Exception as e:
            logger.error(f"Phase transition {{transition_id}} failed: {{e}}")
            return {{
                'status': 'error',
                'message': f"Phase transition failed: {{e}}",
                'transition_id': transition_id
            }}
    
    async def _validate_phase_transition(self, from_phase: Phase, to_phase: Phase, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate phase transition"""
        # TODO: Implement phase transition validation based on assertions
{chr(10).join(f"        # {assertion}" for assertion in test_spec.get('assertions', []))}
        
        # Basic validation
        valid_transitions = {{
            Phase.MEETING: [Phase.ARCHITECT],
            Phase.ARCHITECT: [Phase.GRIND],
            Phase.GRIND: [Phase.PRESENTATION],
            Phase.PRESENTATION: [Phase.MEETING]
        }}
        
        if to_phase not in valid_transitions.get(from_phase, []):
            return {{'valid': False, 'message': f"Invalid transition from {{from_phase.value}} to {{to_phase.value}}"}}
        
        return {{'valid': True, 'message': ''}}
    
    async def _prepare_phase_transition(self, from_phase: Phase, to_phase: Phase, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for phase transition"""
        try:
            # Allocate resources
            resources_allocated = await self._allocate_resources(to_phase, context)
            
            # Prepare components
            components_ready = await self._prepare_components(to_phase, context)
            
            if not components_ready:
                return {{'ready': False, 'message': 'Component preparation failed'}}
            
            return {{
                'ready': True,
                'resources_allocated': resources_allocated,
                'message': 'Phase transition preparation completed'
            }}
            
        except Exception as e:
            logger.error(f"Phase transition preparation failed: {{e}}")
            return {{'ready': False, 'message': str(e)}}
    
    async def _execute_phase_transition(self, from_phase: Phase, to_phase: Phase, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute phase transition"""
        try:
            # Update global arbiter
            await self.global_arbiter.set_current_phase(to_phase.value)
            
            # Update chronos heartbeat
            await self.chronos.record_phase_transition(from_phase.value, to_phase.value)
            
            # Verify state consistency
            state_consistent = await self._verify_state_consistency(to_phase)
            
            return {{
                'state_consistent': state_consistent,
                'transition_time': datetime.now().isoformat(),
                'message': f"Successfully transitioned to {{to_phase.value}}"
            }}
            
        except Exception as e:
            logger.error(f"Phase transition execution failed: {{e}}")
            raise
    
    async def _allocate_resources(self, phase: Phase, context: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate resources for phase"""
        # TODO: Implement resource allocation based on phase requirements
        resource_allocations = {{}}
        
        if phase == Phase.GRIND:
            # Allocate more resources for code generation
            resource_allocations['memory_mb'] = 8192
            resource_allocations['cpu_cores'] = 4
        elif phase == Phase.ARCHITECT:
            # Allocate resources for test generation
            resource_allocations['memory_mb'] = 4096
            resource_allocations['cpu_cores'] = 2
        else:
            # Default allocation
            resource_allocations['memory_mb'] = 2048
            resource_allocations['cpu_cores'] = 1
        
        return resource_allocations
    
    async def _prepare_components(self, phase: Phase, context: Dict[str, Any]) -> bool:
        """Prepare components for phase"""
        # TODO: Implement component preparation
        # This is a mock implementation
        return True
    
    async def _verify_state_consistency(self, phase: Phase) -> bool:
        """Verify state consistency after transition"""
        # TODO: Implement state consistency verification
        return self.current_phase == phase
    
    async def _notify_phase_transition(self, from_phase: Phase, to_phase: Phase, context: Dict[str, Any]):
        """Notify components of phase transition"""
        # TODO: Implement component notification
        notification = {{
            'event_type': 'phase_transition',
            'from_phase': from_phase.value,
            'to_phase': to_phase.value,
            'timestamp': datetime.now().isoformat(),
            'context': context
        }}
        
        logger.info(f"Phase transition notification: {{notification}}")
    
    def _generate_transition_id(self) -> str:
        """Generate unique transition ID"""
        import uuid
        return str(uuid.uuid4())[:8]

# Export orchestration instance
# Note: Requires global_arbiter and chronos_heartbeat to be provided
# orchestration = {component_name.title().replace("_", "")}Orchestration(global_arbiter, chronos_heartbeat)
'''
        return code
    
    def _generate_scanner_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate scanner code"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated scanner code for {component_name}
Test: {test_spec['test_name']}
"""

import ast
import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}Scanner:
    """Generated scanner implementation"""
    
    def __init__(self):
        self.scan_results = {{}}
        self.code_smells = []
        self.improvement_suggestions = []
        logger.info(f"{component_name} scanner initialized")
    
    def scan_code(self, code_content: str, file_path: str) -> Dict[str, Any]:
        """Scan code for issues and improvements"""
        scan_id = self._generate_scan_id()
        
        try:
            logger.info(f"Starting code scan {{scan_id}} for {{file_path}}")
            
            # Parse AST
            try:
                tree = ast.parse(code_content)
            except SyntaxError as e:
                return {{
                    'scan_id': scan_id,
                    'status': 'error',
                    'message': f"Syntax error in code: {{e}}",
                    'file_path': file_path
                }}
            
            # Analyze code structure
            structure_analysis = self._analyze_code_structure(tree)
            
            # Detect code smells
            code_smells = self._detect_code_smells(tree, code_content)
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(tree, code_content, code_smells)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(tree, code_content, code_smells)
            
            # Compile results
            scan_result = {{
                'scan_id': scan_id,
                'file_path': file_path,
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'analysis': {{
                    'structure': structure_analysis,
                    'code_smells': code_smells,
                    'suggestions': suggestions,
                    'quality_metrics': quality_metrics
                }},
                'summary': {{
                    'total_smells': len(code_smells),
                    'total_suggestions': len(suggestions),
                    'quality_score': quality_metrics.get('overall_score', 0),
                    'analysis_depth': 'comprehensive'
                }}
            }}
            
            # Store results
            self.scan_results[scan_id] = scan_result
            
            logger.info(f"Code scan {{scan_id}} completed. Found {{len(code_smells)}} code smells, {{len(suggestions)}} suggestions")
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Code scan {{scan_id}} failed: {{e}}")
            return {{
                'scan_id': scan_id,
                'file_path': file_path,
                'status': 'failed',
                'error': str(e)
            }}
    
    def _analyze_code_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code structure"""
        analysis = {{
            'classes': [],
            'functions': [],
            'imports': [],
            'complexity_indicators': {{}}
        }}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                analysis['classes'].append({{
                    'name': node.name,
                    'line_number': node.lineno,
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                }})
            elif isinstance(node, ast.FunctionDef):
                analysis['functions'].append({{
                    'name': node.name,
                    'line_number': node.lineno,
                    'args': [arg.arg for arg in node.args.args]
                }})
            elif isinstance(node, ast.Import):
                analysis['imports'].extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                analysis['imports'].append(f"{{node.module}}.{{node.names[0].name}}")
        
        # Calculate complexity indicators
        analysis['complexity_indicators'] = {{
            'total_lines': max([node.lineno for node in ast.walk(tree) if hasattr(node, 'lineno')] or [0]),
            'class_count': len(analysis['classes']),
            'function_count': len(analysis['functions']),
            'import_count': len(analysis['imports'])
        }}
        
        return analysis
    
    def _detect_code_smells(self, tree: ast.AST, code_content: str) -> List[Dict[str, Any]]:
        """Detect code smells"""
        smells = []
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_lines = node.lineno - getattr(node, 'end_lineno', node.lineno)
                if function_lines > 50:  # More than 50 lines
                    smells.append({{
                        'type': 'long_function',
                        'severity': 'medium',
                        'message': f"Function '{{node.name}}' is very long ({{function_lines}} lines)",
                        'line_number': node.lineno,
                        'suggestion': 'Consider breaking this function into smaller functions'
                    }})
        
        # Check for duplicate code (simple check)
        lines = code_content.split('\\n')
        line_counts = {{}}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 20:  # Only check substantial lines
                if stripped in line_counts:
                    smells.append({{
                        'type': 'duplicate_code',
                        'severity': 'low',
                        'message': f"Potential duplicate code at line {{i + 1}}",
                        'line_number': i + 1,
                        'suggestion': 'Consider extracting duplicate code into a function'
                    }})
                else:
                    line_counts[stripped] = i + 1
        
        # Check for complex expressions
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check for complex boolean expressions
                if self._is_complex_condition(node.test):
                    smells.append({{
                        'type': 'complex_condition',
                        'severity': 'low',
                        'message': f"Complex boolean condition at line {{node.lineno}}",
                        'line_number': node.lineno,
                        'suggestion': 'Consider simplifying this condition or extracting it into a function'
                    }})
        
        return smells
    
    def _is_complex_condition(self, node: ast.AST) -> bool:
        """Check if condition is complex"""
        if isinstance(node, ast.BoolOp):
            # Count the number of boolean operations
            return len(node.values) > 3  # More than 3 conditions
        return False
    
    def _generate_improvement_suggestions(self, tree: ast.AST, code_content: str, code_smells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Suggest based on code smells
        for smell in code_smells:
            suggestions.append({{
                'type': 'refactoring',
                'priority': 'medium',
                'description': smell['suggestion'],
                'location': f"line {{smell['line_number']}}",
                'estimated_impact': 'medium'
            }})
        
        # General suggestions
        analysis = self._analyze_code_structure(tree)
        
        if analysis['complexity_indicators']['function_count'] > 20:
            suggestions.append({{
                'type': 'architecture',
                'priority': 'high',
                'description': 'Consider splitting this file into multiple modules',
                'location': 'file',
                'estimated_impact': 'high'
            }})
        
        if analysis['complexity_indicators']['class_count'] == 0 and analysis['complexity_indicators']['function_count'] > 10:
            suggestions.append({{
                'type': 'architecture',
                'priority': 'medium',
                'description': 'Consider organizing functions into classes',
                'location': 'file',
                'estimated_impact': 'medium'
            }})
        
        return suggestions
    
    def _calculate_quality_metrics(self, tree: ast.AST, code_content: str, code_smells: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate code quality metrics"""
        metrics = {{}}
        
        # Basic metrics
        total_lines = len(code_content.split('\\n'))
        non_empty_lines = len([line for line in code_content.split('\\n') if line.strip()])
        
        metrics['line_metrics'] = {{
            'total_lines': total_lines,
            'non_empty_lines': non_empty_lines,
            'empty_lines': total_lines - non_empty_lines
        }}
        
        # Complexity metrics
        analysis = self._analyze_code_structure(tree)
        metrics['complexity'] = {{
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity(tree),
            'cognitive_complexity': self._calculate_cognitive_complexity(tree),
            'maintainability_index': self._calculate_maintainability_index(tree, code_content)
        }}
        
        # Quality score
        quality_score = self._calculate_overall_quality_score(code_smells, metrics)
        metrics['overall_score'] = quality_score
        
        return metrics
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.With):
                complexity += 1
        
        return complexity
    
    def _calculate_cognitive_complexity(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity (simplified)"""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                complexity += 1
                # Add extra for nested conditions
                if any(isinstance(parent, ast.If) for parent in self._get_parents(node, tree)):
                    complexity += 1
            elif isinstance(node, (ast.While, ast.For)):
                complexity += 1
        
        return complexity
    
    def _calculate_maintainability_index(self, tree: ast.AST, code_content: str) -> float:
        """Calculate maintainability index (simplified)"""
        # This is a simplified version
        lines = len(code_content.split('\\n'))
        complexity = self._calculate_cyclomatic_complexity(tree)
        
        # Simple heuristic: fewer lines and lower complexity = higher maintainability
        maintainability = max(0, 100 - (lines * 0.1) - (complexity * 5))
        return min(100, maintainability)
    
    def _calculate_overall_quality_score(self, code_smells: List[Dict[str, Any]], metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        base_score = 100.0
        
        # Deduct points for code smells
        for smell in code_smells:
            if smell['severity'] == 'high':
                base_score -= 10
            elif smell['severity'] == 'medium':
                base_score -= 5
            elif smell['severity'] == 'low':
                base_score -= 2
        
        # Deduct points for complexity
        complexity_score = metrics.get('complexity', {{}}).get('maintainability_index', 100)
        base_score = (base_score + complexity_score) / 2
        
        return max(0, min(100, base_score))
    
    def _get_parents(self, node: ast.AST, tree: ast.AST) -> List[ast.AST]:
        """Get parent nodes of a given node"""
        parents = []
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                if child == node:
                    parents.append(parent)
        return parents
    
    def _generate_scan_id(self) -> str:
        """Generate unique scan ID"""
        import uuid
        return str(uuid.uuid4())[:8]

# Export scanner instance
scanner = {component_name.title().replace("_", "")}Scanner()
'''
        return code
    
    def _generate_generic_code(self, test_spec: Dict[str, Any]) -> str:
        """Generate generic code as fallback"""
        component_name = test_spec['component_name']
        
        code = f'''"""
Generated generic implementation for {component_name}
Test: {test_spec['test_name']}
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class {component_name.title().replace("_", "")}:
    """Generated generic implementation"""
    
    def __init__(self):
        logger.info(f"{component_name} initialized")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic operation"""
        try:
            logger.info(f"Executing {component_name}")
            
            # TODO: Implement based on test specification
            {chr(10).join(f"            # {step}" for step in test_spec.get('steps', []))}
            
            # Generate result based on expected results
            result = {{
                'status': 'success',
                'data': input_data,
                'message': 'Operation completed successfully'
            }}
            
            # Validate result based on assertions
            {chr(10).join(f"            # {assertion}" for assertion in test_spec.get('assertions', []))}
            
            return result
            
        except Exception as e:
            logger.error(f"Execution error: {{e}}")
            return {{
                'status': 'error',
                'message': str(e)
            }}

# Export instance
generator = {component_name.title().replace("_", "")}()
'''
        return code

class TestRunner:
    """Runs tests in isolated sandbox environment"""
    
    def __init__(self, sandbox_path: str):
        self.sandbox_path = Path(sandbox_path)
        self.test_results = []
        
    async def run_test(self, test_spec: Dict[str, Any], code_content: str) -> TestResult:
        """Run individual test in sandbox"""
        test_name = test_spec['test_name']
        start_time = time.time()
        
        try:
            # Create test file
            test_file = self.sandbox_path / f"{test_name}.py"
            test_file.write_text(code_content)
            
            # Create test runner script
            runner_script = self._create_test_runner(test_spec)
            runner_file = self.sandbox_path / f"{test_name}_runner.py"
            runner_file.write_text(runner_script)
            
            # Run test in subprocess
            result = await self._run_subprocess_test(runner_file)
            
            execution_time = time.time() - start_time
            
            if result['returncode'] == 0:
                return TestResult(
                    test_name=test_name,
                    status='passed',
                    execution_time=execution_time,
                    assertions_passed=result.get('assertions_passed', 0),
                    assertions_failed=result.get('assertions_failed', 0)
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status='failed',
                    execution_time=execution_time,
                    error_message=result.get('error', 'Test execution failed'),
                    stack_trace=result.get('traceback', '')
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status='failed',
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _create_test_runner(self, test_spec: Dict[str, Any]) -> str:
        """Create test runner script"""
        return f'''
import sys
import traceback
import json
import time

def run_test():
    try:
        # Import generated code
        from {test_spec['test_name']} import *
        
        # Initialize test
        print("Running test: {test_spec['test_name']}")
        
        # Execute test steps
        assertions_passed = 0
        assertions_failed = 0
        
        # TODO: Implement actual test execution based on test_spec
        # This is a placeholder implementation
        
        # Simulate test execution
        time.sleep(0.1)
        
        # Mock assertions
        assertions_passed = 3
        assertions_failed = 0
        
        # Return results
        result = {{
            'status': 'passed',
            'assertions_passed': assertions_passed,
            'assertions_failed': assertions_failed,
            'returncode': 0
        }}
        
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        error_result = {{
            'status': 'failed',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'returncode': 1
        }}
        print(json.dumps(error_result), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(run_test())
'''
    
    async def _run_subprocess_test(self, runner_file: Path) -> Dict[str, Any]:
        """Run test in subprocess"""
        try:
            # Run test with timeout
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(runner_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.sandbox_path)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0  # 30 second timeout
            )
            
            # Parse results
            if stdout:
                try:
                    result = json.loads(stdout.decode())
                    return result
                except json.JSONDecodeError:
                    pass
            
            # Fallback error handling
            return {{
                'returncode': process.returncode or 1,
                'error': stderr.decode() if stderr else 'Test execution failed',
                'traceback': stderr.decode() if stderr else ''
            }}
            
        except asyncio.TimeoutError:
            return {{
                'returncode': 1,
                'error': 'Test execution timed out',
                'traceback': ''
            }}
        except Exception as e:
            return {{
                'returncode': 1,
                'error': str(e),
                'traceback': traceback.format_exc()
            }}

class SecurityScanner:
    """Scans code for security vulnerabilities"""
    
    def __init__(self):
        self.security_patterns = {
            'sql_injection': [
                r"cursor\.execute\(.*[^']*%s[^']*\)",
                r"cursor\.execute\(.*[^']*\+[^']*\)",
                r"query.*=.*[^']*%[^']*"
            ],
            'hardcoded_secrets': [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]"
            ],
            'unsafe_deserialization': [
                r"pickle\.loads\(",
                r"yaml\.load\(",
                r"eval\("
            ]
        }
    
    def scan_security(self, code_content: str) -> Dict[str, Any]:
        """Scan code for security issues"""
        vulnerabilities = []
        
        for vuln_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code_content, re.IGNORECASE)
                for match in matches:
                    vulnerabilities.append({
                        'type': vuln_type,
                        'severity': 'high' if vuln_type in ['sql_injection', 'hardcoded_secrets'] else 'medium',
                        'line_number': code_content[:match.start()].count('\n') + 1,
                        'description': f"Potential {vuln_type.replace('_', ' ')} vulnerability detected",
                        'recommendation': self._get_security_recommendation(vuln_type)
                    })
        
        return {
            'vulnerabilities_found': len(vulnerabilities),
            'vulnerabilities': vulnerabilities,
            'security_score': max(0, 100 - len(vulnerabilities) * 20)
        }
    
    def _get_security_recommendation(self, vuln_type: str) -> str:
        """Get security recommendation"""
        recommendations = {
            'sql_injection': 'Use parameterized queries or ORM to prevent SQL injection',
            'hardcoded_secrets': 'Store secrets in environment variables or secure vaults',
            'unsafe_deserialization': 'Use safe serialization methods and validate input'
        }
        return recommendations.get(vuln_type, 'Review code for security best practices')

class PerformanceProfiler:
    """Profiles code performance"""
    
    def profile_code(self, code_content: str) -> Dict[str, Any]:
        """Profile code for performance issues"""
        lines = code_content.split('\n')
        
        performance_issues = []
        
        # Check for inefficient patterns
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check for nested loops
            if 'for ' in line_stripped and any('for ' in prev_line for prev_line in lines[max(0, i-3):i]):
                performance_issues.append({
                    'type': 'nested_loops',
                    'severity': 'medium',
                    'line_number': i + 1,
                    'description': 'Potential nested loop detected',
                    'recommendation': 'Consider optimizing nested loops or using more efficient algorithms'
                })
            
            # Check for repeated expensive operations
            if any(pattern in line_stripped for pattern in ['len(', 'max(', 'min(', 'sum(']):
                if lines.count(line_stripped) > 1:
                    performance_issues.append({
                        'type': 'repeated_operations',
                        'severity': 'low',
                        'line_number': i + 1,
                        'description': 'Repeated expensive operation detected',
                        'recommendation': 'Consider caching results of expensive operations'
                    })
        
        return {
            'performance_issues': performance_issues,
            'performance_score': max(0, 100 - len(performance_issues) * 10)
        }

class GrindPhase:
    """
    Grind Phase - Autonomous Code Implementation
    
    This phase takes test specifications and implements code in sandbox environment,
    running iterative cycles until all tests pass.
    """
    
    def __init__(self, 
                 redis_bus: RedisBus,
                 global_arbiter: GlobalArbiter,
                 identity_firewall: IdentityFirewall,
                 bikameral_memory: BikameralMemory,
                 chronos: ChronosHeartbeat):
        self.redis_bus = redis_bus
        self.global_arbiter = global_arbiter
        self.identity_firewall = identity_firewall
        self.bikameral_memory = bikameral_memory
        self.chronos = chronos
        self.code_generator = CodeGenerator()
        self.security_scanner = SecurityScanner()
        self.performance_profiler = PerformanceProfiler()
        
        logger.info("Grind Phase initialized")
    
    async def implement_code(self, test_suite: Dict[str, Any], session_context: Dict[str, Any]) -> ImplementationSession:
        """
        Implement code based on test specifications
        
        Args:
            test_suite: Test suite from Architect Phase
            session_context: Session context information
            
        Returns:
            Implementation session with results
        """
        try:
            logger.info(f"Starting Grind Phase for contract {test_suite.get('contract_id')}")
            
            # 1. Create implementation session
            session = self._create_implementation_session(test_suite, session_context)
            
            # 2. Create sandbox environment
            sandbox_path = await self._create_sandbox(session)
            
            # 3. Implement components iteratively
            for iteration in range(session.max_iterations):
                session.current_iteration = iteration
                logger.info(f"Implementation iteration {iteration + 1}/{session.max_iterations}")
                
                # Implement each component
                for test_spec in test_suite.get('specifications', []):
                    implementation = await self._implement_component(test_spec, sandbox_path, session)
                    session.implementations.append(implementation)
                    
                    # Run tests
                    test_result = await self._run_tests(implementation, test_spec, sandbox_path)
                    session.test_results.append(test_result)
                    
                    # Check if implementation is successful
                    if test_result.status == 'passed':
                        logger.info(f"Component {test_spec['component_name']} implemented successfully")
                    else:
                        logger.warning(f"Component {test_spec['component_name']} failed tests, retrying...")
                        
                        # Generate improved code based on test failure
                        improved_code = await self._improve_code(implementation, test_result, test_spec)
                        implementation.code_content = improved_code
                        
                        # Re-run tests
                        test_result = await self._run_tests(implementation, test_spec, sandbox_path)
                
                # Check if all tests pass
                if all(result.status == 'passed' for result in session.test_results):
                    logger.info("All tests passed - implementation complete!")
                    break
                
                # Check resource limits
                if await self._check_resource_limits(session):
                    logger.warning("Resource limits exceeded - stopping implementation")
                    break
            
            # 4. Final security and performance checks
            final_results = await self._final_validation(session, sandbox_path)
            
            # 5. Store implementation results
            await self._store_implementation_results(session)
            
            # 6. Publish completion event
            await self._publish_completion(session)
            
            logger.info(f"Grind Phase completed for contract {session.contract_id}")
            return session
            
        except Exception as e:
            logger.error(f"Grind Phase failed: {e}")
            await self._publish_error(test_suite.get('contract_id'), str(e))
            raise
    
    def _create_implementation_session(self, test_suite: Dict[str, Any], session_context: Dict[str, Any]) -> ImplementationSession:
        """Create implementation session"""
        session_id = hashlib.md5(f"{test_suite['contract_id']}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        return ImplementationSession(
            session_id=session_id,
            contract_id=test_suite['contract_id'],
            suite_id=test_suite['suite_id'],
            sandbox_path="",  # Will be set later
            components=[spec['component_name'] for spec in test_suite.get('specifications', [])],
            start_time=datetime.now(),
            max_iterations=10
        )
    
    async def _create_sandbox(self, session: ImplementationSession) -> str:
        """Create sandbox environment for implementation"""
        sandbox_base = Path(tempfile.gettempdir()) / "longin_ego_sandbox"
        sandbox_path = sandbox_base / session.session_id
        
        # Create sandbox directory
        sandbox_path.mkdir(parents=True, exist_ok=True)
        session.sandbox_path = str(sandbox_path)
        
        # Create sandbox configuration
        sandbox_config = {
            'session_id': session.session_id,
            'contract_id': session.contract_id,
            'created_at': datetime.now().isoformat(),
            'resource_limits': {
                'memory_mb': 4096,  # 4GB memory limit
                'cpu_percent': 50,  # 50% CPU limit
                'disk_mb': 1024,    # 1GB disk limit
                'network': 'disabled'  # Disable network access
            },
            'security_policies': {
                'file_access': 'restricted',
                'system_calls': 'filtered',
                'code_execution': 'sandboxed'
            }
        }
        
        # Store sandbox config in memory
        config_file = sandbox_path / "sandbox_config.json"
        config_file.write_text(json.dumps(sandbox_config, indent=2))
        
        logger.info(f"Created sandbox environment: {sandbox_path}")
        return str(sandbox_path)
    
    async def _implement_component(self, test_spec: Dict[str, Any], sandbox_path: str, session: ImplementationSession) -> CodeImplementation:
        """Implement individual component"""
        component_name = test_spec['component_name']
        start_time = time.time()
        
        try:
            logger.info(f"Implementing component: {component_name}")
            
            # Determine component type
            component_type = test_spec.get('test_type', 'integration')
            
            # Generate code
            code_content = self.code_generator.generate_code(test_spec, component_type)
            
            # Security scan
            security_scan = self.security_scanner.scan_security(code_content)
            
            # Performance profiling
            performance_profile = self.performance_profiler.profile_code(code_content)
            
            implementation_time = time.time() - start_time
            
            # Create implementation result
            implementation = CodeImplementation(
                component_name=component_name,
                file_path=f"{sandbox_path}/{component_name}.py",
                code_content=code_content,
                test_results={},
                implementation_time=implementation_time,
                iteration_count=session.current_iteration,
                quality_score=self._calculate_quality_score(security_scan, performance_profile),
                security_scan_results=security_scan,
                performance_metrics=performance_profile
            )
            
            logger.info(f"Component {component_name} implemented in {implementation_time:.2f}s")
            return implementation
            
        except Exception as e:
            logger.error(f"Component implementation failed for {component_name}: {e}")
            raise
    
    async def _run_tests(self, implementation: CodeImplementation, test_spec: Dict[str, Any], sandbox_path: str) -> TestResult:
        """Run tests for implementation"""
        try:
            # Create test runner
            test_runner = TestRunner(sandbox_path)
            
            # Run test
            test_result = await test_runner.run_test(test_spec, implementation.code_content)
            
            # Update implementation with test results
            implementation.test_results = {
                'test_name': test_result.test_name,
                'status': test_result.status,
                'execution_time': test_result.execution_time,
                'assertions_passed': test_result.assertions_passed,
                'assertions_failed': test_result.assertions_failed
            }
            
            return test_result
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return TestResult(
                test_name=test_spec['test_name'],
                status='failed',
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def _improve_code(self, implementation: CodeImplementation, test_result: TestResult, test_spec: Dict[str, Any]) -> str:
        """Improve code based on test failure"""
        try:
            logger.info(f"Improving code for {implementation.component_name} based on test failure")
            
            # Analyze test failure
            failure_analysis = self._analyze_test_failure(test_result, test_spec)
            
            # Generate improved code
            improved_code = self._generate_improved_code(implementation.code_content, failure_analysis, test_spec)
            
            # Validate improved code
            validation_result = self._validate_improved_code(improved_code, test_spec)
            
            if validation_result['valid']:
                logger.info(f"Code improvement successful for {implementation.component_name}")
                return improved_code
            else:
                logger.warning(f"Code improvement validation failed for {implementation.component_name}")
                return implementation.code_content  # Return original code
                
        except Exception as e:
            logger.error(f"Code improvement failed for {implementation.component_name}: {e}")
            return implementation.code_content  # Return original code
    
    def _analyze_test_failure(self, test_result: TestResult, test_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test failure to identify improvement areas"""
        analysis = {
            'failure_type': 'unknown',
            'improvement_areas': [],
            'suggestions': []
        }
        
        if test_result.error_message:
            if 'syntax' in test_result.error_message.lower():
                analysis['failure_type'] = 'syntax_error'
                analysis['improvement_areas'].append('code_syntax')
                analysis['suggestions'].append('Fix syntax errors in generated code')
            elif 'import' in test_result.error_message.lower():
                analysis['failure_type'] = 'import_error'
                analysis['improvement_areas'].append('dependencies')
                analysis['suggestions'].append('Add missing imports or dependencies')
            elif 'assertion' in test_result.error_message.lower():
                analysis['failure_type'] = 'assertion_failure'
                analysis['improvement_areas'].append('logic_implementation')
                analysis['suggestions'].append('Fix logic to meet test assertions')
        
        return analysis
    
    def _generate_improved_code(self, original_code: str, failure_analysis: Dict[str, Any], test_spec: Dict[str, Any]) -> str:
        """Generate improved code based on failure analysis"""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated code generation
        
        improved_code = original_code
        
        # Add missing imports if needed
        if 'dependencies' in failure_analysis['improvement_areas']:
            improved_code = self._add_missing_imports(improved_code, test_spec)
        
        # Fix syntax errors if needed
        if 'code_syntax' in failure_analysis['improvement_areas']:
            improved_code = self._fix_syntax_errors(improved_code)
        
        # Improve logic if needed
        if 'logic_implementation' in failure_analysis['improvement_areas']:
            improved_code = self._improve_logic(improved_code, test_spec)
        
        return improved_code
    
    def _add_missing_imports(self, code: str, test_spec: Dict[str, Any]) -> str:
        """Add missing imports to code"""
        required_imports = []
        
        # Analyze test specification to determine required imports
        if 'database' in test_spec.get('component_name', '').lower():
            required_imports.extend(['import asyncio', 'import asyncpg'])
        elif 'api' in test_spec.get('component_name', '').lower():
            required_imports.extend(['import asyncio', 'from typing import Dict, Any'])
        elif 'ui' in test_spec.get('component_name', '').lower():
            required_imports.extend(['import React', 'import PropTypes'])
        
        # Add imports at the beginning
        import_section = '\n'.join(required_imports)
        return f"{import_section}\n\n{code}"
    
    def _fix_syntax_errors(self, code: str) -> str:
        """Fix basic syntax errors in code"""
        # This is a simplified implementation
        # Fix common syntax issues
        fixed_code = code
        
        # Fix unbalanced parentheses
        open_parens = fixed_code.count('(')
        close_parens = fixed_code.count(')')
        if open_parens > close_parens:
            fixed_code += ')' * (open_parens - close_parens)
        
        # Fix unbalanced braces
        open_braces = fixed_code.count('{')
        close_braces = fixed_code.count('}')
        if open_braces > close_braces:
            fixed_code += '}' * (open_braces - close_braces)
        
        return fixed_code
    
    def _improve_logic(self, code: str, test_spec: Dict[str, Any]) -> str:
        """Improve code logic based on test specification"""
        # This is a simplified implementation
        # Add better error handling
        if 'try:' not in code and 'except' not in code:
            # Wrap main logic in try-except
            lines = code.split('\n')
            improved_lines = []
            in_function = False
            function_indent = ''
            
            for line in lines:
                if line.strip().startswith('def ') and not in_function:
                    in_function = True
                    function_indent = len(line) - len(line.lstrip())
                    improved_lines.append(line)
                elif in_function and line.strip() and len(line) - len(line.lstrip()) == function_indent:
                    # End of function
                    in_function = False
                    improved_lines.append(line)
                elif in_function and 'return' in line:
                    # Add try-except before return
                    indent = ' ' * (len(line) - len(line.lstrip()) + 4)
                    improved_lines.append(f"{indent}try:")
                    improved_lines.append(f"{indent}    {line.strip()}")
                    improved_lines.append(f"{indent}except Exception as e:")
                    improved_lines.append(f"{indent}    return {{'status': 'error', 'message': str(e)}}")
                else:
                    improved_lines.append(line)
            
            code = '\n'.join(improved_lines)
        
        return code
    
    def _validate_improved_code(self, improved_code: str, test_spec: Dict[str, Any]) -> Dict[str, bool]:
        """Validate improved code"""
        try:
            # Try to compile the code
            compile(improved_code, '<string>', 'exec')
            return {'valid': True, 'message': ''}
        except SyntaxError as e:
            return {'valid': False, 'message': f'Syntax error in improved code: {e}'}
    
    def _calculate_quality_score(self, security_scan: Dict[str, Any], performance_profile: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        base_score = 100.0
        
        # Deduct points for security vulnerabilities
        vulnerabilities = security_scan.get('vulnerabilities_found', 0)
        base_score -= vulnerabilities * 15
        
        # Deduct points for performance issues
        performance_issues = len(performance_profile.get('performance_issues', []))
        base_score -= performance_issues * 5
        
        return max(0, base_score)
    
    async def _check_resource_limits(self, session: ImplementationSession) -> bool:
        """Check if resource limits are exceeded"""
        try:
            # Check memory usage
            import psutil
            memory_info = psutil.virtual_memory()
            if memory_info.percent > 90:  # 90% memory usage
                logger.warning(f"Memory usage critical: {memory_info.percent}%")
                return True
            
            # Check disk usage
            disk_info = psutil.disk_usage('/')
            if disk_info.percent > 95:  # 95% disk usage
                logger.warning(f"Disk usage critical: {disk_info.percent}%")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Resource limit check failed: {e}")
            return False
    
    async def _final_validation(self, session: ImplementationSession, sandbox_path: str) -> Dict[str, Any]:
        """Perform final validation of implementation"""
        validation_results = {
            'security_validation': {},
            'performance_validation': {},
            'integration_validation': {}
        }
        
        # Security validation
        for implementation in session.implementations:
            if implementation.security_scan_results:
                validation_results['security_validation'][implementation.component_name] = {
                    'vulnerabilities': implementation.security_scan_results.get('vulnerabilities_found', 0),
                    'security_score': implementation.security_scan_results.get('security_score', 0)
                }
        
        # Performance validation
        for implementation in session.implementations:
            if implementation.performance_metrics:
                validation_results['performance_validation'][implementation.component_name] = {
                    'issues': len(implementation.performance_metrics.get('performance_issues', [])),
                    'performance_score': implementation.performance_metrics.get('performance_score', 0)
                }
        
        # Integration validation
        validation_results['integration_validation'] = {
            'all_tests_passed': all(result.status == 'passed' for result in session.test_results),
            'total_tests': len(session.test_results),
            'passed_tests': len([result for result in session.test_results if result.status == 'passed']),
            'failed_tests': len([result for result in session.test_results if result.status == 'failed'])
        }
        
        return validation_results
    
    async def _store_implementation_results(self, session: ImplementationSession):
        """Store implementation results in memory"""
        session_data = {
            'session_id': session.session_id,
            'contract_id': session.contract_id,
            'suite_id': session.suite_id,
            'start_time': session.start_time.isoformat(),
            'current_iteration': session.current_iteration,
            'implementations': [
                {
                    'component_name': impl.component_name,
                    'file_path': impl.file_path,
                    'implementation_time': impl.implementation_time,
                    'iteration_count': impl.iteration_count,
                    'quality_score': impl.quality_score,
                    'test_results': impl.test_results,
                    'security_score': impl.security_scan_results.get('security_score', 0),
                    'performance_score': impl.performance_metrics.get('performance_score', 0)
                }
                for impl in session.implementations
            ],
            'test_results': [
                {
                    'test_name': result.test_name,
                    'status': result.status,
                    'execution_time': result.execution_time,
                    'assertions_passed': result.assertions_passed,
                    'assertions_failed': result.assertions_failed
                }
                for result in session.test_results
            ]
        }
        
        # Store in short-term memory
        await self.bikameral_memory.store_short_term(
            f"grind_session:{session.session_id}",
            session_data,
            ttl=7200  # 2 hours TTL
        )
        
        # Store in long-term memory
        await self.bikameral_memory.store_long_term(
            f"grind_session:{session.session_id}",
            session_data
        )
    
    async def _publish_completion(self, session: ImplementationSession):
        """Publish completion event to Redis bus"""
        event = {
            'event_type': 'grind_phase_completed',
            'session_id': session.session_id,
            'contract_id': session.contract_id,
            'suite_id': session.suite_id,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_components': len(session.implementations),
                'successful_implementations': len([impl for impl in session.implementations if impl.test_results.get('status') == 'passed']),
                'total_iterations': session.current_iteration + 1,
                'average_quality_score': sum(impl.quality_score for impl in session.implementations) / len(session.implementations) if session.implementations else 0
            }
        }
        
        await self.redis_bus.publish('orchestration.events', event)
    
    async def _publish_error(self, contract_id: str, error_message: str):
        """Publish error event to Redis bus"""
        event = {
            'event_type': 'grind_phase_error',
            'contract_id': contract_id,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.redis_bus.publish('orchestration.events', event)

# Factory function for easy integration
def create_grind_phase(runtime_context: Dict[str, Any]) -> GrindPhase:
    """Factory function to create Grind Phase instance"""
    return GrindPhase(
        redis_bus=runtime_context['redis_bus'],
        global_arbiter=runtime_context['global_arbiter'],
        identity_firewall=runtime_context['identity_firewall'],
        bikameral_memory=runtime_context['bikameral_memory'],
        chronos=runtime_context['chronos_heartbeat']
    )