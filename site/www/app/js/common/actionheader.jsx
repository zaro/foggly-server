import React from 'react';
import { Alert } from 'react-bootstrap';


export default
class ActionHeader extends React.Component {
  static defaultProps = {
  }
  static propTypes = {
    buttons: React.PropTypes.arrayOf(React.PropTypes.object),
  }
  state = { errorMessage: null }

  getErrorMessage() {
    if (this.state.errorMessage) {
      return (
        <Alert bsStyle="danger" onDismiss={this.dismissError}>
          <pre style={{ color: 'inherit', text: 'inherit', background: 'inherit' }}>{this.state.errorMessage}</pre>
        </Alert>
      );
    }
    return undefined;
  }

  dismissError = () => {
    this.setState({ errorMessage: null });
  }

  showError = (errorMessage) => {
    this.setState({ errorMessage });
  }

  makeButtonId(button) {
    if (button.key) {
      return button.key;
    }
    const t = button.title ?
      button.title : (
        button.name ?
        button.name :
        Math.floor((Math.random() * 10000000) + 1)
      );
    return t.replace(/\s/g, '-').toLowerCase();
  }

  render() {
    return (
      <div>
        {this.getErrorMessage()}
        <div className="bs-component pull-right">
        {
          this.props.buttons.map(
            (b) => <a key={this.makeButtonId(b)} className="btn btn-raised btn-primary btn-xs" title={b.title} href="#" onClick={b.onClick}>{b.name}</a>
          )
        }
        </div>
      </div>
    );
  }
}
