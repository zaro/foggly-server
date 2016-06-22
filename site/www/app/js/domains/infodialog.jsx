import React from 'react';
import apiCall from '../common/apicall';
import ReactDOM from 'react-dom';

import { Button, Modal, Label, InputGroup, FormControl, FormGroup, ControlLabel, Grid, Row, Col } from 'react-bootstrap';

export default class InfoDialog extends React.Component {
  static propTypes = {
    onClose: React.PropTypes.func,
    onSubmit: React.PropTypes.func,
    title: React.PropTypes.string,
    children: React.PropTypes.node,
    domain: React.PropTypes.string.isRequired,
  };

  state = {
    showModal: false,
    working: true,
    error: null,
    config: {},
  }


  show = () => {
    this.setState({ showModal: true, working: true });
    this.serverRequest = apiCall(`/api/domains/config?domain=${this.props.domain}`);
    this.serverRequest.then((data) => {
      console.info('config Done : %o', data);
      this.setState({ showModal: true, working: false, config: data.response[0] });
    }).catch((error) => {
      console.error('destroyDomain Error : %o', error);
      this.setState({ working: false, error });
    });
  }

  close = () => {
    this.setState({ showModal: false });
    if (this.serverRequest) {
      this.serverRequest.abort();
    }
    if (this.props.onClose) {
      this.props.onClose();
    }
  }

  copyToClipboard(refName) {
    const node = ReactDOM.findDOMNode(this.refs[refName]);
    if ( node ) {
      node.select();
      if (!document.execCommand('copy')) {
        console.error('Failed to copy to clipboard!');
      }
    }
  }

  render() {
    const cfg = this.state.config;
    const dcfg = this.state.config.config || {};
    const sshConfigSnippet = `Host ${cfg.domain}
        Port ${dcfg.SSH_PORT}
        User user
    `;
    return (
      <Modal show={this.state.showModal} onHide={this.close}>
        <Modal.Header closeButton>
          <Modal.Title>{this.props.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Grid>
            <Row>
              <Col sd={2} md={2} lg={2}>Domain <Label>{cfg.domain}</Label><br /></Col>
              <Col sd={2} md={2} lg={2}>Application <Label>{cfg.type}</Label><br /></Col>
              <Col sd={2} md={2} lg={2}>URL: <a href={`http://${cfg.domain}`} target="_blank">{cfg.domain}</a></Col>
            </Row>
          </Grid>
          <FormGroup>
            <InputGroup>
              <ControlLabel>Ssh Command</ControlLabel>
              <FormControl readOnly ref="sshCommand" value={`ssh -p ${dcfg.SSH_PORT} user@${cfg.domain}`} />
              <InputGroup.Button>
                <Button bsStyle="default" onClick={() => this.copyToClipboard('sshCommand')}><i className="material-icons">content_copy</i></Button>
              </InputGroup.Button>
            </InputGroup>
            <InputGroup>
              <ControlLabel>Git Remote URL</ControlLabel>
              <FormControl readOnly ref="gitRemoteUrl" value={`ssh://user@${cfg.domain}:${dcfg.SSH_PORT}/www`} />
              <InputGroup.Button>
                <Button bsStyle="default" onClick={() => this.copyToClipboard('gitRemoteUrl')}><i className="material-icons">content_copy</i></Button>
              </InputGroup.Button>
            </InputGroup>
            <InputGroup>
              <ControlLabel>.ssh/config snippet</ControlLabel>
              <FormControl componentClass="textarea" rows={4} readOnly ref="sshConfigSnippet" value={sshConfigSnippet} />
              <InputGroup.Button>
                <Button bsStyle="default" onClick={() => this.copyToClipboard('sshConfigSnippet')}><i className="material-icons">content_copy</i></Button>
              </InputGroup.Button>
            </InputGroup>
          </FormGroup>
          <Button active type="submit" onClick={this.close} bsStyle="default" className="btn-raised pull-right">
            Close
          </Button>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>
    );
  }
}
