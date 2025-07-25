import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import Papa from 'papaparse';
import _ from 'lodash';

const CropProductionEDA = () => {
  const [data, setData] = useState([]);
  const [processedData, setProcessedData] = useState({});
  const [selectedCommodity, setSelectedCommodity] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const csvData = await window.fs.readFile('crop_production_processed.csv', { encoding: 'utf8' });
        
        const parsed = Papa.parse(csvData, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          delimitersToGuess: [',', '\t', '|', ';']
        });

        // Clean headers
        const cleanedData = parsed.data.map(row => {
          const cleanedRow = {};
          Object.keys(row).forEach(key => {
            const cleanKey = key.trim();
            cleanedRow[cleanKey] = row[key];
          });
          return cleanedRow;
        });

        // Convert date strings to proper dates and extract year
        const dataWithDates = cleanedData.map(row => ({
          ...row,
          date: new Date(row.date),
          year: new Date(row.date).getFullYear(),
          value: parseFloat(row.value) || 0
        }));

        setData(dataWithDates);
        processDataForAnalysis(dataWithDates);
        setLoading(false);
      } catch (error) {
        console.error('Error loading data:', error);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const processDataForAnalysis = (rawData) => {
    // Group by commodity
    const byCommodity = _.groupBy(rawData, 'commodity');
    
    // Calculate summary statistics
    const summaryStats = {};
    Object.keys(byCommodity).forEach(commodity => {
      const values = byCommodity[commodity].map(d => d.value).filter(v => v > 0);
      summaryStats[commodity] = {
        count: values.length,
        mean: _.mean(values),
        median: values.sort((a, b) => a - b)[Math.floor(values.length / 2)],
        min: _.min(values),
        max: _.max(values),
        std: Math.sqrt(_.sum(values.map(v => Math.pow(v - _.mean(values), 2))) / values.length),
        unit: byCommodity[commodity][0]?.unit || 'Unknown'
      };
    });

    // Time series data for each commodity
    const timeSeriesData = {};
    Object.keys(byCommodity).forEach(commodity => {
      timeSeriesData[commodity] = byCommodity[commodity]
        .sort((a, b) => a.year - b.year)
        .map(d => ({
          year: d.year,
          value: d.value,
          commodity: d.commodity,
          unit: d.unit
        }));
    });

    // Growth rates
    const growthRates = {};
    Object.keys(timeSeriesData).forEach(commodity => {
      const series = timeSeriesData[commodity];
      const firstValue = series[0]?.value || 0;
      const lastValue = series[series.length - 1]?.value || 0;
      const years = series.length;
      
      growthRates[commodity] = {
        totalGrowth: ((lastValue - firstValue) / firstValue * 100).toFixed(2),
        annualGrowthRate: (Math.pow(lastValue / firstValue, 1 / years) - 1) * 100
      };
    });

    // Latest production values for comparison
    const latestProduction = {};
    Object.keys(byCommodity).forEach(commodity => {
      const latest = _.maxBy(byCommodity[commodity], 'year');
      latestProduction[commodity] = {
        value: latest.value,
        year: latest.year,
        unit: latest.unit
      };
    });

    setProcessedData({
      summaryStats,
      timeSeriesData,
      growthRates,
      latestProduction,
      commodities: Object.keys(byCommodity)
    });
  };

  if (loading) {
    return <div className="p-8 text-center">Loading data...</div>;
  }

  if (data.length === 0) {
    return <div className="p-8 text-center text-red-600">No data available</div>;
  }

  const { summaryStats, timeSeriesData, growthRates, latestProduction, commodities } = processedData;

  // Colors for different commodities
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#8dd1e1', '#d084d0'];

  // Data for current view
  const currentTimeSeriesData = selectedCommodity === 'All' 
    ? timeSeriesData[commodities[0]] || []
    : timeSeriesData[selectedCommodity] || [];

  // Combined data for all commodities comparison
  const combinedData = commodities.length > 0 ? 
    _.unionBy(...commodities.map(commodity => 
      (timeSeriesData[commodity] || []).map(d => ({ year: d.year }))
    ), 'year')
    .sort((a, b) => a.year - b.year)
    .map(yearData => {
      const result = { year: yearData.year };
      commodities.forEach(commodity => {
        const dataPoint = (timeSeriesData[commodity] || []).find(d => d.year === yearData.year);
        result[commodity] = dataPoint ? dataPoint.value : null;
      });
      return result;
    }) : [];

  // Latest production data for pie chart
  const pieData = commodities.map((commodity, index) => ({
    name: commodity,
    value: latestProduction[commodity]?.value || 0,
    unit: latestProduction[commodity]?.unit || '',
    color: colors[index % colors.length]
  })).filter(d => d.value > 0);

  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Global Crop Production Analysis (2000-2025)</h1>
      
      {/* Data Overview */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">Dataset Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-800">Total Records</h3>
            <p className="text-2xl font-bold text-blue-600">{data.length}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-medium text-green-800">Commodities</h3>
            <p className="text-2xl font-bold text-green-600">{commodities.length}</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-medium text-purple-800">Years Covered</h3>
            <p className="text-2xl font-bold text-purple-600">2000-2025</p>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <h3 className="font-medium text-orange-800">Data Source</h3>
            <p className="text-lg font-bold text-orange-600">USDA PSD</p>
          </div>
        </div>
      </div>

      {/* Summary Statistics Table */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">Summary Statistics by Commodity</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full table-auto">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 text-left">Commodity</th>
                <th className="px-4 py-2 text-right">Unit</th>
                <th className="px-4 py-2 text-right">Mean</th>
                <th className="px-4 py-2 text-right">Min</th>
                <th className="px-4 py-2 text-right">Max</th>
                <th className="px-4 py-2 text-right">Growth Rate</th>
              </tr>
            </thead>
            <tbody>
              {commodities.map((commodity, index) => (
                <tr key={commodity} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="px-4 py-2 font-medium">{commodity}</td>
                  <td className="px-4 py-2 text-right text-sm">{summaryStats[commodity]?.unit}</td>
                  <td className="px-4 py-2 text-right">{summaryStats[commodity]?.mean.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className="px-4 py-2 text-right">{summaryStats[commodity]?.min.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className="px-4 py-2 text-right">{summaryStats[commodity]?.max.toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                  <td className="px-4 py-2 text-right">
                    <span className={`font-medium ${parseFloat(growthRates[commodity]?.totalGrowth) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {growthRates[commodity]?.totalGrowth}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Time Series Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-semibold text-gray-700">Production Trends Over Time</h2>
          <select 
            value={selectedCommodity} 
            onChange={(e) => setSelectedCommodity(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Commodities</option>
            {commodities.map(commodity => (
              <option key={commodity} value={commodity}>{commodity}</option>
            ))}
          </select>
        </div>
        
        <ResponsiveContainer width="100%" height={400}>
          {selectedCommodity === 'All' ? (
            <LineChart data={combinedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value, name) => [
                value ? value.toLocaleString() : 'N/A', 
                name
              ]} />
              <Legend />
              {commodities.map((commodity, index) => (
                <Line 
                  key={commodity}
                  type="monotone" 
                  dataKey={commodity} 
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  connectNulls={false}
                />
              ))}
            </LineChart>
          ) : (
            <LineChart data={currentTimeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => [value.toLocaleString(), selectedCommodity]} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#8884d8" 
                strokeWidth={3}
                name={selectedCommodity}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* Latest Production Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">Latest Production Values (2024-2025)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={pieData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip formatter={(value, name, props) => [
                `${value.toLocaleString()} ${props.payload.unit}`,
                name
              ]} />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">Growth Rate Comparison (2000-2025)</h2>
          <div className="space-y-3">
            {commodities.map((commodity, index) => {
              const growth = parseFloat(growthRates[commodity]?.totalGrowth || 0);
              return (
                <div key={commodity} className="flex items-center justify-between">
                  <span className="font-medium">{commodity}</span>
                  <div className="flex items-center">
                    <div className={`w-24 h-4 rounded-full mr-2 ${growth >= 0 ? 'bg-green-200' : 'bg-red-200'}`}>
                      <div 
                        className={`h-4 rounded-full ${growth >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.min(Math.abs(growth), 100)}%` }}
                      ></div>
                    </div>
                    <span className={`font-bold ${growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {growth.toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Key Insights */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gray-700">Key Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-800 mb-2">Highest Growth</h3>
            <p className="text-sm">
              {commodities.reduce((max, commodity) => 
                parseFloat(growthRates[commodity]?.totalGrowth || 0) > parseFloat(growthRates[max]?.totalGrowth || 0) ? commodity : max
              )} shows the highest growth rate
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-800 mb-2">Largest Producer</h3>
            <p className="text-sm">
              {pieData.reduce((max, item) => item.value > max.value ? item : max, pieData[0] || {}).name} has the highest current production
            </p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-800 mb-2">Data Quality</h3>
            <p className="text-sm">
              Complete dataset with {data.length} records covering 6 major commodities over 25+ years
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CropProductionEDA;