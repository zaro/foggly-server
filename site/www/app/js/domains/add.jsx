/* global _ */
import React from 'react';
import apiCall from '../common/apicall';
import { ButtonInput, Modal, Input, Alert } from 'react-bootstrap';

export default class DomainAdd extends React.Component {
  static propTypes = {
    onClose: React.PropTypes.func.isRequired,
  };

  constructor(props) {
    super(props);
    this.state = {
      showModal: true,
      working: false,
      valid: false,
      error: null,
    };
  }
  show = () => {
    this.setState({ showModal: true, working: false, error: null });
  }

  close = () => {
    this.setState({ showModal: false, working: false });
    if (this.props.onClose) {
      this.props.onClose();
    }
  }

  submit = (e) => {
    e.preventDefault();
    this.addDomain();
  }

  validate = () => {
    const domain = this.refs.domainName.getValue();
    const appType = this.refs.appType.getValue();
    this.setState({
      valid: domain.length > 0 && appType.length > 0,
    });
  }

  addDomain() {
    this.setState({ working: true, error: null });
    const postData = {
      domain: this.refs.domainName.getValue(),
      app_type: this.refs.appType.getValue(),
      host: this.refs.host.getValue(),
    };
    console.log('Adding domain:', postData);
    apiCall('/api/domains/add', postData, { method: 'POST' }).then((_data) => {
      this.close();
    }).catch((data, error, textStatus) => {
      console.log(data);
      console.log(textStatus);
      console.log(error);
      this.setState({ showModal: true, working: false, error: data.error });
    });
  }

  render() {
    let spinner: string;
    let error;
    if (this.state.working) {
      spinner = <i className="fa fa-spinner fa-spin"></i>;
    }
    if (this.state.error && this.state.error.length) {
      error = (
        <Alert bsStyle="danger">
          {this.state.error}
        </Alert>
      );
    }
    return (
      <Modal show={this.state.showModal} onHide={this.close}>
        <Modal.Header closeButton>
          <Modal.Title>Add domain {spinner}</Modal.Title>
          {error}
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={this.submit}>
            <Input disabled={this.state.working} onChange={this.validate}
              label="Domain name" className="form-control" placeholder="Fully qualified domain name" ref="domainName" type="text"
            />
            <Input disabled={this.state.working} onChange={this.validate} type="select" label="Application type" ref="appType">
              <option key="no-app" value="">Select applicaiton type</option>
              {_.map(window.fConfig.appTypes, (v, k) => <option key={k} value={k}>{v}</option> )}
            </Input>
            <Input disabled={this.state.working} onChange={this.validate} type="select" label="Host" ref="host">
              <option key="no-app" value="">Select host for this domain</option>
              {_.map(window.fConfig.hosts, (v, k) => <option key={k} value={k}>{v}</option> )}
            </Input>
            <ButtonInput disabled={!this.state.valid} active type="submit" onClick={this.submit} value="Submit" bsStyle="default" />
          </form>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>
    );
  }
}
