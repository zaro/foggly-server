/* global _ */
import React from 'react';
import apiCall from '../common/apicall';
import InputDialog from '../common/inputdialog';
import { FormGroup, FormControl, ControlLabel, Label } from 'react-bootstrap';

export default
class DomainAddPublikKey extends InputDialog {

  validate = () => {
    let valid = true;
    for (const refName of ['publicKey']) {
      valid = valid && (this.getInputValue(refName).length > 0);
    }
    this.setState({ valid });
  }

  onSubmit() {
    this.setState({ working: true, error: null });
    const postData = {
      domain: this.props.data.domain,
      publicKey: this.getInputValue('publicKey'),
    };
    console.log('Adding domain:', postData);
    apiCall('/api/domains/publickey', postData, { method: 'PUT' }).then((_data) => {
      this.close();
    }).catch((error) => {
      console.error(error);
      this.setState({ showModal: true, working: false, error });
    });
  }

  renderInputs() {
    return [
      <div key="label">Domain <Label>{this.props.data.domain}</Label></div>,
      <FormGroup key="publicKey">
        <ControlLabel>Public Key to add</ControlLabel>
        <FormControl
          disabled={this.state.working} onChange={this.validate}
          placeholder="Ssh public key" ref="publicKey" componentClass="textarea"
        />
      </FormGroup>,
    ];
  }
}
