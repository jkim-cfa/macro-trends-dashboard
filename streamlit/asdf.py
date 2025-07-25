import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, ScatterPlot, Scatter } from 'recharts';
import { FileText, TrendingUp, AlertTriangle, Calendar, DollarSign, Shield } from 'lucide-react';
import * as Papa from 'papaparse';

const DefenseEDA = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [contractsData, setContractsData] = useState([]);
  const [sipriData, setSipriData] = useState([]);

  useEffect(() => {
    // Load SIPRI data
    const sipriCSV = `report,year,topic,insight,sector
SIPRI,2025,Military Spending,Global military spending reached a record high of $2.7 trillion in 2024.,defence
SIPRI,2025,Conflict-Related Deaths,"Conflict-related deaths surged to 239,000 in 2024.",defence
SIPRI,2025,Climate Change & Security,2024 was the first year with average global temperatures exceeding 1.5°C above pre-industrial levels.,defence
SIPRI,2025,Geopolitical Instability,"The Russia-Ukraine war intensified, and other conflicts escalated or persisted in 2024.",defence
SIPRI,2025,Nuclear Arms Race,"Nuclear arms reductions ended in 2024, raising concerns about a new arms race.",defence
SIPRI,2025,Arms Production & Transfers,Significant increases in arms production and transfers were observed in Europe and Asia in 2024.,defence
SIPRI,2025,Nuclear Weapons Modernization,The report details nuclear weapons modernization efforts in 2024.,defence
SIPRI,2025,Arms Control Challenges,Significant challenges persist in enforcing existing arms control treaties and addressing emerging threats in 2024.,defence
SIPRI,2025,Emerging Military Technologies,"Emerging technologies like AI, cyber warfare, and space-based weaponry are highlighted as significant concerns in 2024.",defence`;

    const contractsCSV = `date,indicator,value,insight,category
2025-08-01,"L-SAM 양산(발사대,ABM)",731937714445.0,,High-Value (≥ 10B KRW)
2025-08-01,L-SAM 양산(다기능레이더),505901459516.0,,Frequent Items (6 times)
2025-07-01,천마 체계 외주정비(방산),208379067864.0,,High-Value (≥ 10B KRW)
2025-08-01,장애물개척전차 2차 양산,203623631149.0,,Frequent Items (6 times)
2025-08-01,"L-SAM 양산(통제소,AAM,체계통합)",140632280000.0,,High-Value (≥ 10B KRW)
2025-07-01,155mm 단위장약 등,72904819200.0,,Frequent Items (7 times)
2025-07-01,F- 기관 부품(D),52177368076.0,,High-Value (≥ 10B KRW)
2025-08-01,"엔진,디젤식(장개차용)",38760000000.0,,Frequent Items (3 times)
2025-07-01,C-130/CN-2 기관/모듈 창정비(D),35073290162.0,,High-Value (≥ 10B KRW)
2025-08-01,KUH-1 헬기 엔진 (제조),34787848662.0,,Frequent Items (3 times)
2025-07-01,천무유도탄 부품류(방산),30099253700.0,,High-Value (≥ 10B KRW)
2025-07-01,천무유도탄 로켓부품(방산),24960090266.0,,Frequent Items (4 times)
2025-07-01,120밀리 전차 도비방지 연습예광탄,22326912000.0,,High-Value (≥ 10B KRW)
2025-07-01,천무유도탄 수명연장 외주정비,18656521728.0,,Frequent Items (4 times)
2025-08-01,천마 유도탄 체계 정비(방산),18381708864.0,,Frequent Items (4 times)
2025-07-01,105밀리 연습예광탄,15899506000.0,,High-Value (≥ 10B KRW)
2025-08-01,잠수함 연료전지체계(제조),15362600000.0,,High-Value (≥ 10B KRW)
2025-07-01,충격신관,15285313200.0,,High-Value (≥ 10B KRW)
2025-07-01,KF- RAM COATING 및 외부전면도장(D),13375520600.13,,High-Value (≥ 10B KRW)
2025-07-01,UH- 기체 창정비,12763235000.0,,High-Value (≥ 10B KRW)
2025-08-01,해상감시레이더-II PBL 2차,12435925000.0,,Frequent Items (7 times)
2025-08-01,F-16D Wiring Harness 정비(D),10337745810.0,,High-Value (≥ 10B KRW)
2025-07-01,비호 감지기 유니트 등(구매),9715202940.0,,Frequent Items (3 times)
2025-07-01,12.7밀리 파쇄탄,9295445504.0,,Frequent Items (8 times)
2025-07-01,"방탄복, 조끼용(대)",8419200114.0,,Frequent Items (5 times)
2025-07-01,"트럭,승강식,항공기 적재용(KMJ-1C)",7481200000.0,,Frequent Items (3 times)
2025-08-01,검독수리-B Batch-II 정비대체장비(76mm함포),6804400000.0,,Frequent Items (7 times)
2025-08-01,76mm 함포(5번함) 창정비,5428960000.0,,Frequent Items (7 times)
2025-07-01,"트럭,승강식,항공기 적재용(KMHU-83D/E)",5400000000.0,,Frequent Items (3 times)
2025-07-01,30밀리 탄약류,5052298640.0,,Frequent Items (8 times)
2025-07-01,장갑차 변속기 외주정비,4891648000.0,,Frequent Items (5 times)
2025-07-01,"천궁, 천궁II 작전수행능력 개선(통제소)",4800000000.0,,Frequent Items (7 times)
2025-07-01,차륜형장갑차 성능개량 체계개발,4775000000.0,,Frequent Items (5 times)
2025-08-01,12.7mm원격사격통제체계(검독수리-B B-II 9 12번함용),4639444794.0,,Frequent Items (7 times)
2025-08-01,회전익 기체(CH-47) 수송용 정비,3760062592.0,,Frequent Items (3 times)
2025-07-01,105/155밀리 훈련탄,3607783216.0,,Frequent Items (8 times)
2025-07-01,"방탄복, 조끼용(특대)",3351927906.0,,Frequent Items (5 times)
2025-08-01,"항공기 급유차(6,500G/L)",3150000000.0,,Frequent Items (3 times)
2025-08-01,발칸 총열부 부품(방산),3136133474.0,,Frequent Items (7 times)
2025-07-01,"155밀리 훈련용 추진장약통(5호,6호)",3055525000.0,,Frequent Items (8 times)
2025-07-01,155밀리 연습용 대전차지뢰살포탄,2838067000.0,,Frequent Items (8 times)
2025-08-01,회전익 기체(AH-1S) 구성품 정비,2575530043.96,,Frequent Items (3 times)
2025-08-01,(500MD) 회전익 기체 정비,2332174800.0,,Frequent Items (3 times)
2025-07-01,"방탄복, 조끼용(중)",2227323286.0,,Frequent Items (5 times)
2025-08-01,발칸 송탄기 부품(방산),1912372441.0,,Frequent Items (7 times)
2025-07-01,120mm 자주박격포 적재훈련탄,1875168000.0,,Frequent Items (7 times)
2025-08-01,K55자주포 엔진 외주정비,1856570880.0,,Frequent Items (3 times)
2025-08-01,천무유도탄 제어부,1728884000.0,,Frequent Items (4 times)
2025-07-01,K21장갑차 사통장치 외주정비,1610655585.0,,Frequent Items (5 times)
2025-07-01,"천궁, 천궁II 작전수행능력 개선(다기능레이더)",1580000000.0,,Frequent Items (7 times)
2025-08-01,"철매-II 성능개량 (2차 양산) 수송차량(크레인, 종합)",1569000000.0,,Frequent Items (7 times)
2025-07-01,"방탄복, 조끼용(해병)",1525437200.0,,Frequent Items (5 times)
2025-07-01,비호 주전원공급기 정비,1508466870.0,,Frequent Items (3 times)
2025-07-01,"방탄복, 조끼용(소)",1435256942.0,,Frequent Items (5 times)
2025-07-01,K 교육훈련용 장갑차 외주정비,1366686091.0,,Frequent Items (5 times)
2025-08-01,비호 레이다부품 정비(방산),1257716664.0,,Frequent Items (3 times)
2025-07-01,76밀리 연습탄 K245(KC114),1253395800.0,,Frequent Items (8 times)
2025-07-01,"발칸 구동유니트, 전기 유압식 등 4항목 정비",1172604492.0,,Frequent Items (7 times)
2025-08-01,천궁 시험세트(방산),1166078000.0,,Frequent Items (5 times)
2025-08-01,발칸 사격통제부 부품(방산),1064192407.0,,Frequent Items (7 times)
2025-07-01,"회로카드조립체(전차,장갑차,상륙장갑차)",1057353952.0,,Frequent Items (5 times)
2025-08-01,"() 권총,9mm,반자동식,K5",931380372.0,,Frequent Items (7 times)
2025-07-01,장갑차 부품,892484124.0,,Frequent Items (5 times)
2025-07-01,대공표적기 지원용역(천마),869934562.0,,Frequent Items (4 times)
2025-08-01,철매-II 성능개량 (2차 양산) 수송차량(K-918),858200000.0,,Frequent Items (7 times)
2025-07-01,발칸 자이로스코프(연구개발),856173635.0,,Frequent Items (7 times)
2025-07-01,30mm 차륜형대공포 2차양산 일반공구,823785353.0,,Frequent Items (7 times)
2025-08-01,성능개량 위치보고접속장치 수리부속(구매),640730406.0,,Frequent Items (4 times)
2025-08-01,발칸 사격제어부 부품,588566403.0,,Frequent Items (7 times)
2025-07-01,천마 궤도 정비(방산),559376400.0,,Frequent Items (4 times)
2025-08-01,"40밀리포 부품류, 보병전투차량용",545317041.0,,Frequent Items (8 times)
2025-07-01,발칸 축전식 전지(제조),544050000.0,,Frequent Items (7 times)
2025-08-01,"방열기, 엔진냉각제용",535951182.0,,Frequent Items (3 times)
2025-07-01,(긴급) 축 등 10종,64398400.0,,Emergency Procurement
2025-07-01,"(긴급)냉각기, 공기식, 전자장비용 1종",55600000.0,,Emergency Procurement`;

    Papa.parse(sipriCSV, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => setSipriData(results.data)
    });

    Papa.parse(contractsCSV, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      complete: (results) => setContractsData(results.data)
    });
  }, []);

  // Data processing functions
  const getContractValueDistribution = () => {
    const valueRanges = [
      { range: '< 1B KRW', min: 0, max: 1000000000, count: 0 },
      { range: '1-10B KRW', min: 1000000000, max: 10000000000, count: 0 },
      { range: '10-50B KRW', min: 10000000000, max: 50000000000, count: 0 },
      { range: '50-100B KRW', min: 50000000000, max: 100000000000, count: 0 },
      { range: '> 100B KRW', min: 100000000000, max: Infinity, count: 0 }
    ];

    contractsData.forEach(contract => {
      const value = contract.value;
      valueRanges.forEach(range => {
        if (value >= range.min && value < range.max) {
          range.count++;
        }
      });
    });

    return valueRanges;
  };

  const getCategoryBreakdown = () => {
    const categories = {};
    contractsData.forEach(contract => {
      const category = contract.category || 'Other';
      if (!categories[category]) {
        categories[category] = { count: 0, totalValue: 0 };
      }
      categories[category].count++;
      categories[category].totalValue += contract.value || 0;
    });

    return Object.entries(categories).map(([name, data]) => ({
      name,
      count: data.count,
      totalValue: data.totalValue,
      avgValue: data.totalValue / data.count
    }));
  };

  const getTopicAnalysis = () => {
    const topics = {};
    sipriData.forEach(item => {
      const topic = item.topic;
      if (!topics[topic]) {
        topics[topic] = 0;
      }
      topics[topic]++;
    });

    return Object.entries(topics).map(([topic, count]) => ({ topic, count }));
  };

  const getTimelineTrends = () => {
    const timeline = {};
    contractsData.forEach(contract => {
      const month = contract.date ? contract.date.substring(0, 7) : '2025-07';
      if (!timeline[month]) {
        timeline[month] = { month, totalValue: 0, count: 0 };
      }
      timeline[month].totalValue += contract.value || 0;
      timeline[month].count++;
    });

    return Object.values(timeline).sort((a, b) => a.month.localeCompare(b.month));
  };

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

  const TabButton = ({ id, label, icon: Icon, active, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
        active ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
      }`}
    >
      <Icon size={16} />
      <span>{label}</span>
    </button>
  );

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Defense Data EDA Dashboard</h1>
      
      {/* Navigation */}
      <div className="flex space-x-4 mb-6">
        <TabButton
          id="overview"
          label="Overview"
          icon={FileText}
          active={activeTab === 'overview'}
          onClick={setActiveTab}
        />
        <TabButton
          id="contracts"
          label="Contract Analysis"
          icon={DollarSign}
          active={activeTab === 'contracts'}
          onClick={setActiveTab}
        />
        <TabButton
          id="trends"
          label="Trends & Patterns"
          icon={TrendingUp}
          active={activeTab === 'trends'}
          onClick={setActiveTab}
        />
        <TabButton
          id="insights"
          label="Security Insights"
          icon={Shield}
          active={activeTab === 'insights'}
          onClick={setActiveTab}
        />
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Dataset Summary</h2>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold">SIPRI Global Security Data</h3>
                <p className="text-gray-600">{sipriData.length} security insights covering military spending, conflicts, and emerging threats</p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <h3 className="font-semibold">Defense Contracts Data</h3>
                <p className="text-gray-600">{contractsData.length} defense procurement contracts with values and categories</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Key Statistics</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">$2.7T</div>
                <div className="text-sm text-gray-600">Global Military Spending 2024</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">239K</div>
                <div className="text-sm text-gray-600">Conflict Deaths 2024</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {contractsData.reduce((sum, c) => sum + (c.value || 0), 0).toLocaleString('en', {notation: 'compact'})}
                </div>
                <div className="text-sm text-gray-600">Total Contract Value (KRW)</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {contractsData.filter(c => c.category === 'High-Value (≥ 10B KRW)').length}
                </div>
                <div className="text-sm text-gray-600">High-Value Contracts</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Contract Analysis Tab */}
      {activeTab === 'contracts' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Contract Value Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getContractValueDistribution()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Category Breakdown</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={getCategoryBreakdown()}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                  label={({ name, count }) => `${name}: ${count}`}
                >
                  {getCategoryBreakdown().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold mb-4">Top 10 Highest Value Contracts</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Contract</th>
                    <th className="text-right p-2">Value (KRW)</th>
                    <th className="text-center p-2">Category</th>
                    <th className="text-center p-2">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {contractsData
                    .sort((a, b) => (b.value || 0) - (a.value || 0))
                    .slice(0, 10)
                    .map((contract, i) => (
                      <tr key={i} className="border-b hover:bg-gray-50">
                        <td className="p-2 font-medium">{contract.indicator}</td>
                        <td className="p-2 text-right">{(contract.value || 0).toLocaleString()}</td>
                        <td className="p-2 text-center">
                          <span className={`px-2 py-1 rounded text-xs ${
                            contract.category?.includes('High-Value') ? 'bg-red-100 text-red-800' :
                            contract.category?.includes('Frequent') ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {contract.category}
                          </span>
                        </td>
                        <td className="p-2 text-center">{contract.date}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Trends Tab */}
      {activeTab === 'trends' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Monthly Contract Trends</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={getTimelineTrends()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [value.toLocaleString(), 'Total Value (KRW)']} />
                <Line type="monotone" dataKey="totalValue" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Security Topics Coverage</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getTopicAnalysis()} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="topic" type="category" width={150} />
                <Tooltip />
                <Bar dataKey="count" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold mb-4">Contract Categories vs. Values</h2>
            <ResponsiveContainer width="100%" height={400}>
              <ScatterPlot
                data={contractsData.map(c => ({
                  value: c.value || 0,
                  frequency: parseInt(c.category?.match(/\d+/)?.[0] || 1),
                  category: c.category,
                  name: c.indicator
                }))}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="frequency" 
                  name="Frequency"
                  label={{ value: 'Frequency (times)', position: 'insideBottom', offset: -5 }}
                />
                <YAxis 
                  dataKey="value" 
                  name="Value"
                  scale="log"
                  domain={['dataMin', 'dataMax']}
                  label={{ value: 'Contract Value (KRW)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'value' ? value.toLocaleString() : value,
                    name === 'value' ? 'Value (KRW)' : 'Frequency'
                  ]}
                />
                <Scatter dataKey="value" fill="#8884d8" />
              </ScatterPlot>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Security Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {sipriData.map((insight, i) => (
              <div key={i} className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="text-red-500 mt-1" size={20} />
                  <div>
                    <h3 className="font-semibold text-lg mb-2">{insight.topic}</h3>
                    <p className="text-gray-700 text-sm leading-relaxed">{insight.insight}</p>
                    <div className="mt-3 text-xs text-gray-500">
                      {insight.report} • {insight.year}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Key Findings & Correlations</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="font-semibold">Contract Patterns</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>• L-SAM (Land-based Surface-to-Air Missile) systems dominate high-value contracts</li>
                  <li>• Strong focus on air defense and missile systems procurement</li>
                  <li>• Significant investment in vehicle maintenance and modernization</li>
                  <li>• Emergency procurement items suggest urgent operational needs</li>
                </ul>
              </div>
              <div className="space-y-4">
                <h3 className="font-semibold">Global Security Context</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>• Record military spending aligns with increased regional tensions</li>
                  <li>• Focus on emerging technologies (AI, cyber, space weapons)</li>
                  <li>• Climate change adding new dimension to security challenges</li>
                  <li>• Arms control treaties facing significant enforcement challenges</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DefenseEDA