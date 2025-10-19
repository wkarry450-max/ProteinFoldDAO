// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ProteinFoldingDAO
 * @dev 去中心化蛋白折叠预测DAO智能合约
 * @author ProteinFoldDAO Team
 */
contract ProteinFoldingDAO is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter;
    
    // 预测结构体
    struct Prediction {
        uint256 id;
        address submitter;
        string sequence;
        uint256 stabilityScore; // 乘以1000存储，避免小数
        uint256 voteCount;
        uint256 timestamp;
        bool isValid;
    }
    
    // 投票记录
    struct Vote {
        address voter;
        uint256 predictionId;
        uint256 timestamp;
    }
    
    // 状态变量
    Counters.Counter private _predictionIds;
    mapping(uint256 => Prediction) public predictions;
    mapping(address => mapping(uint256 => bool)) public hasVoted;
    mapping(address => uint256) public userVoteCount;
    
    // 事件
    event NewPrediction(
        uint256 indexed id,
        address indexed submitter,
        string sequence,
        uint256 stabilityScore,
        uint256 timestamp
    );
    
    event VoteCast(
        address indexed voter,
        uint256 indexed predictionId,
        uint256 timestamp
    );
    
    event PredictionUpdated(
        uint256 indexed id,
        uint256 newVoteCount
    );
    
    // 常量
    uint256 public constant MAX_VOTES_PER_USER = 100;
    uint256 public constant MIN_SEQUENCE_LENGTH = 10;
    uint256 public constant MAX_SEQUENCE_LENGTH = 1000;
    uint256 public constant STABILITY_SCORE_MULTIPLIER = 1000;
    
    constructor() {
        // 合约部署者成为所有者
    }
    
    /**
     * @dev 提交蛋白折叠预测
     * @param _sequence 氨基酸序列
     * @param _stabilityScore 稳定性分数 (0-1000, 对应0.000-1.000)
     */
    function submitPrediction(
        string memory _sequence,
        uint256 _stabilityScore
    ) external nonReentrant {
        require(bytes(_sequence).length >= MIN_SEQUENCE_LENGTH, "序列太短");
        require(bytes(_sequence).length <= MAX_SEQUENCE_LENGTH, "序列太长");
        require(_stabilityScore <= STABILITY_SCORE_MULTIPLIER, "稳定性分数无效");
        
        // 验证序列只包含有效氨基酸
        require(_isValidSequence(_sequence), "序列包含无效字符");
        
        _predictionIds.increment();
        uint256 newId = _predictionIds.current();
        
        predictions[newId] = Prediction({
            id: newId,
            submitter: msg.sender,
            sequence: _sequence,
            stabilityScore: _stabilityScore,
            voteCount: 0,
            timestamp: block.timestamp,
            isValid: true
        });
        
        emit NewPrediction(
            newId,
            msg.sender,
            _sequence,
            _stabilityScore,
            block.timestamp
        );
    }
    
    /**
     * @dev 对预测进行投票
     * @param _predictionId 预测ID
     */
    function vote(uint256 _predictionId) external nonReentrant {
        require(_predictionId > 0 && _predictionId <= _predictionIds.current(), "预测ID无效");
        require(predictions[_predictionId].isValid, "预测已失效");
        require(!hasVoted[msg.sender][_predictionId], "已经投票过");
        require(userVoteCount[msg.sender] < MAX_VOTES_PER_USER, "投票次数超限");
        
        predictions[_predictionId].voteCount++;
        hasVoted[msg.sender][_predictionId] = true;
        userVoteCount[msg.sender]++;
        
        emit VoteCast(msg.sender, _predictionId, block.timestamp);
        emit PredictionUpdated(_predictionId, predictions[_predictionId].voteCount);
    }
    
    /**
     * @dev 获取预测详情
     * @param _predictionId 预测ID
     * @return prediction 预测结构体
     */
    function getPrediction(uint256 _predictionId) external view returns (Prediction memory prediction) {
        require(_predictionId > 0 && _predictionId <= _predictionIds.current(), "预测ID无效");
        return predictions[_predictionId];
    }
    
    /**
     * @dev 获取所有预测ID
     * @return ids 预测ID数组
     */
    function getAllPredictionIds() external view returns (uint256[] memory ids) {
        uint256 total = _predictionIds.current();
        ids = new uint256[](total);
        
        for (uint256 i = 1; i <= total; i++) {
            ids[i - 1] = i;
        }
    }
    
    /**
     * @dev 获取用户提交的预测
     * @param _user 用户地址
     * @return userPredictions 用户预测数组
     */
    function getUserPredictions(address _user) external view returns (uint256[] memory userPredictions) {
        uint256 total = _predictionIds.current();
        uint256 count = 0;
        
        // 计算用户预测数量
        for (uint256 i = 1; i <= total; i++) {
            if (predictions[i].submitter == _user) {
                count++;
            }
        }
        
        userPredictions = new uint256[](count);
        uint256 index = 0;
        
        // 填充用户预测ID
        for (uint256 i = 1; i <= total; i++) {
            if (predictions[i].submitter == _user) {
                userPredictions[index] = i;
                index++;
            }
        }
    }
    
    /**
     * @dev 获取最受欢迎的预测
     * @param _limit 返回数量限制
     * @return topPredictions 最受欢迎预测数组
     */
    function getTopPredictions(uint256 _limit) external view returns (uint256[] memory topPredictions) {
        uint256 total = _predictionIds.current();
        if (total == 0) {
            return new uint256[](0);
        }
        
        // 创建ID数组并排序
        uint256[] memory ids = new uint256[](total);
        for (uint256 i = 1; i <= total; i++) {
            ids[i - 1] = i;
        }
        
        // 简单冒泡排序按票数降序
        for (uint256 i = 0; i < total - 1; i++) {
            for (uint256 j = 0; j < total - i - 1; j++) {
                if (predictions[ids[j]].voteCount < predictions[ids[j + 1]].voteCount) {
                    uint256 temp = ids[j];
                    ids[j] = ids[j + 1];
                    ids[j + 1] = temp;
                }
            }
        }
        
        // 返回前_limit个
        uint256 returnCount = _limit > total ? total : _limit;
        topPredictions = new uint256[](returnCount);
        
        for (uint256 i = 0; i < returnCount; i++) {
            topPredictions[i] = ids[i];
        }
    }
    
    /**
     * @dev 获取合约统计信息
     * @return totalPredictions 总预测数
     * @return totalVotes 总投票数
     */
    function getStats() external view returns (uint256 totalPredictions, uint256 totalVotes) {
        totalPredictions = _predictionIds.current();
        totalVotes = 0;
        
        for (uint256 i = 1; i <= totalPredictions; i++) {
            totalVotes += predictions[i].voteCount;
        }
    }
    
    /**
     * @dev 验证氨基酸序列格式
     * @param _sequence 序列字符串
     * @return isValid 是否有效
     */
    function _isValidSequence(string memory _sequence) internal pure returns (bool isValid) {
        bytes memory sequenceBytes = bytes(_sequence);
        
        for (uint256 i = 0; i < sequenceBytes.length; i++) {
            bytes1 char = sequenceBytes[i];
            // 检查是否为有效氨基酸字符 (A-Z)
            if (char < 0x41 || char > 0x5A) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * @dev 管理员功能：使预测失效
     * @param _predictionId 预测ID
     */
    function invalidatePrediction(uint256 _predictionId) external onlyOwner {
        require(_predictionId > 0 && _predictionId <= _predictionIds.current(), "预测ID无效");
        predictions[_predictionId].isValid = false;
    }
    
    /**
     * @dev 管理员功能：重置用户投票计数
     * @param _user 用户地址
     */
    function resetUserVotes(address _user) external onlyOwner {
        userVoteCount[_user] = 0;
    }
}

