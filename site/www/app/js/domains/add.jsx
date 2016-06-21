/* global _ */
import React from 'react';
import apiCall from '../common/apicall';
import InputDialog from '../common/inputdialog';
import { FormGroup, FormControl, ControlLabel } from 'react-bootstrap';

export default
class DatabaseAdd extends InputDialog {

  validate = () => {
    let valid = true;
    for (const refName of ['domainName', 'appType', 'host']) {
      valid = valid && (this.getInputValue(refName).length > 0);
    }
    this.setState({ valid });
  }

  onSubmit() {
    this.setState({ working: true, error: null });
    const postData = {
      domain: this.getInputValue('domainName'),
      app_type: this.getInputValue('appType'),
      host: this.getInputValue('host'),
    };
    console.log('Adding domain:', postData);
    apiCall('/api/domains/add', postData, { method: 'POST' }).then((_data) => {
      this.close();
    }).catch((error) => {
      console.error(error);
      this.setState({ showModal: true, working: false, error });
    });
  }

  renderInputs() {
    return [
      <FormGroup key="domainName">
        <ControlLabel>Domain name</ControlLabel>
        <FormControl
          disabled={this.state.working} onChange={this.validate}
          placeholder="Fully qualified domain name" ref="domainName" type="text"
        />
      </FormGroup>,
      <FormGroup key="appType">
        <ControlLabel>Application type</ControlLabel>
        <FormControl disabled={this.state.working} onChange={this.validate} componentClass="select" ref="appType">
          <option key="" value="">Select applicaiton type</option>
          {_.map(window.fConfig.appTypes, (v, k) => <option key={k} value={k}>{v}</option> )}
        </FormControl>
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
