import React from 'react';
import apiCall from '../common/apicall';
import InputDialog from '../common/inputdialog';
import { FormGroup, FormControl, ControlLabel } from 'react-bootstrap';

export default
class DatabaseAdd extends InputDialog {

  onSubmit() {
    this.setState({ working: true, error: null });
    const postData = {};
    for (const refName of ['db_name', 'db_user', 'db_pass', 'host']) {
      postData[refName] = this.getInputValue(refName);
    }
    console.log('Adding database:', postData);
    apiCall('/api/databases/mysql/add', postData, { method: 'POST' }).then((_data) => {
      this.close();
    }).catch((error) => {
      const err = error.error ? error.error : error;
      console.error(err);
      this.setState({ showModal: true, working: false, error: err });
    });
  }

  validate = () => {
    let valid = true;
    for (const refName of ['db_name', 'db_user', 'db_pass', 'host']) {
      valid = valid && (this.getInputValue(refName).length > 0);
    }
    this.setState({ valid });
  }

  renderInputs() {
    return [
      <FormGroup key="db_name">
        <ControlLabel>Database name</ControlLabel>
        <FormControl
          disabled={this.state.working} onChange={this.validate}
          placeholder="Database name" ref="db_name" type="text"
        />
      </FormGroup>,
      <FormGroup key="db_user">
        <ControlLabel>Database user</ControlLabel>
        <FormControl
          disabled={this.state.working} onChange={this.validate}
          placeholder="Username" ref="db_user" type="text"
        />
      </FormGroup>,
      <FormGroup key="db_pass">
        <ControlLabel>Database password</ControlLabel>
        <FormControl
          disabled={this.state.working} onChange={this.validate}
          className="form-control" placeholder="Password" ref="db_pass" type="text"
        />
      </FormGroup>,
      <FormGroup key="host">
        <ControlLabel>Host</ControlLabel>
        <FormControl disabled={this.state.working} onChange={this.validate} componentClass="select" ref="host">
          <option key="" value="">Select host for this database</option>
          {_.map(window.fConfig.hosts, (v, k) => <option key={k} value={k}>{v}</option> )}
        </FormControl>
      </FormGroup>,
    ];
  }

}
