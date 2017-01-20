import React from 'react';
import { Button, Modal } from 'react-bootstrap';

export default class ConfirmDialog extends React.Component {
  static propTypes = {
    onClose: React.PropTypes.func,
    onSubmit: React.PropTypes.func,
    title: React.PropTypes.string,
    children: React.PropTypes.node,
    danger: React.PropTypes.bool,
  };

  state = {
    showModal: false,
  }


  show = () => {
    this.setState({ showModal: true });
  }

  close = () => {
    this.setState({ showModal: false });
    if (this.props.onClose) {
      this.props.onClose();
    }
  }

  submit = (e) => {
    e.preventDefault();
    if (this.props.onSubmit) {
      this.props.onSubmit();
    }
    this.setState({ showModal: false });
  }


  render() {
    const bsStyle = this.props.danger ? 'danger' : 'primary';
    return (
      <Modal show={this.state.showModal} onHide={this.close}>
        <Modal.Header closeButton>
          <Modal.Title>{this.props.title}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div>
            {this.props.children}
          </div>
          <Button active type="submit" onClick={this.close} className="btn-raised">
            Cancel
          </Button>
          <Button active type="submit" onClick={this.submit} bsStyle={bsStyle} className="btn-raised pull-right">
            Submit
          </Button>
        </Modal.Body>
      </Modal>
    );
  }
}
