var path = require("path")
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')
var ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
  context: __dirname,

  entry: {
      domainstable: './app/js/domainstable',
      vendor: ["./app/css/vendor.js", "react", "react-dom", "jquery", "lodash", "bootstrap", "bootstrap-material-design"],
  }, // entry point of our app. app/js/index.js should require other js modules and dependencies it needs

  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name].js",
    chunkFilename: "[id].js"
    //filename: "[name]-[hash].js",
  },

  plugins: [
    new webpack.ResolverPlugin(
      new webpack.ResolverPlugin.DirectoryDescriptionFilePlugin("bower.json", ["main"])
    ),
    new webpack.ProvidePlugin({
      _ : "lodash",
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": "jquery"
    }),
    new BundleTracker({
      filename: './webpack-stats.json'
    }),
    new webpack.optimize.CommonsChunkPlugin(/* chunkName= */"vendor", /* filename= */"vendor.bundle.js"),
    new ExtractTextPlugin("[name].css"),
  ],

  module: {
    //preLoaders: [
    //  {
    //    test: /\.(js|css)$/,
    //    loader: "source-map-loader"
    //  }
    //],
    loaders: [{
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'react']
        }
      }, // to transform JSX into JS
      {
        test: /\.css$/,
        loader: ExtractTextPlugin.extract("style-loader","css-loader")
      },
      { test: /\.(ttf|eot|svg|woff2|woff)(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: "file-loader" },
    ],
  },

  resolve: {
    modulesDirectories: ['node_modules', 'bower_components'],
    extensions: ['', '.js', '.jsx', '.css']
  },
  devtool: "#source-map"
}
