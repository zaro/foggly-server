import React from 'react';
import apiCall from '../common/apicall';
import {GenericTable} from '../common/table';

class DatabasesHeader extends React.Component {
  render() {
    return (
      <tr>
        <th>#</th>
        <th>database</th>
        <th>user</th>
        <th>password</th>
        <th>actions</th>
      </tr>
    )

  }
}

class DatabasesRow extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      working: false
    }
  }
  deleteDatabase() {
    console.log('Delete database:', this.props.db_name);
    this.setState({working: true});
    apiCall('/api/databases/mysql', {
      db_name: this.props.db_name,
      db_user: this.props.db_user
    }, {method: "DELETE"}).then((data) => {
      console.log('DDONE', data);
      this.props.removeRow(this.props._id)
    }).catch((data, error, textStatus) => {
      console.log(data);
      console.log(textStatus);
      console.log(error);
      this.setState({working: false});
    });
  }
  render() {
    let style={}
    if(this.state.working){
      style.textDecoration = 'line-through'
    }
    return (
      <tr style={style}>
        <td>{this.state.working ? <i className='fa fa-spinner fa-spin'></i> : null }</td>
        <td>{this.props.db_name}</td>
        <td>{this.props.db_user}</td>
        <td>{this.props.db_pass}</td>
        <td>
          <a className="btn btn-raised btn-primary btn-xs" title="Delete database" href="#" onClick={(e) => this.deleteDatabase(e)}>delete</a>
        </td>
      </tr>
    )
  }
}

export default
class DatabasesTable extends GenericTable {
  static defaultProps = {
    headerRowComponent: DatabasesHeader,
    rowComponent: DatabasesRow,
    columns: 4
  };
  constructor(props) {
    super(props);
  }
  fetch() {
    this.serverRequest = apiCall('/api/databases/mysql');
    this.setState({loading: true})
    this.serverRequest.then((data) => {
      let dataList = _.forEach(data.response, (value)=>{
        value._id = value.db_name + value.db_user;
      });
      this.setState({dataList: dataList, loading: false});
      this.serverRequest = null;
    }).catch((data, errorThrown, textStatus) => {
      console.log(data);
      console.log(textStatus);
      console.log(errorThrown);
      this.setState({loading: false});
      this.serverRequest = null;
    });
  }
  cancelFetch() {
    if (this.serverRequest) {
      this.serverRequest.abort()
    }
  }
}
