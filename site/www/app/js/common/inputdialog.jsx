import React from 'react';
import ReactDOM from 'react-dom';
import { Button, Modal, Alert } from 'react-bootstrap';

export default class InputDialog extends React.Component {
  static propTypes = {
    onClose: React.PropTypes.func,
    onSubmit: React.PropTypes.func,
    title: React.PropTypes.string,
    data: React.PropTypes.object,
  };

  state = {
    showModal: false,
    working: false,
    valid: false,
    error: null,
  }

  getInputValue(refName) {
    const node = ReactDOM.findDOMNode(this.refs[refName]);
    if ( node ) {
      return node.value;
    }
    throw new Error(`Invalid ref name : ${refName}`);
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
    if (this.props.onSubmit) {
      this.props.onSubmit();
    }
    if (this.onSubmit) {
      this.onSubmit();
    }
  }

  validate = () => {
    this.setState({
      valid: false,
    });
  }

  renderInputs() {
    return (<div>Implement renderInputs() in subclass</div>);
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
          <Modal.Title>{this.props.title}{spinner}</Modal.Title>
          {error}
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={this.submit}>
            {this.renderInputs()}
            <Button disabled={!this.state.valid} active type="submit" onClick={this.submit} bsStyle="default" className="btn-raised">
              Submit
            </Button>
          </form>
        </Modal.Body>
        <Modal.Footer></Modal.Footer>
      </Modal>
    );
  }
}
