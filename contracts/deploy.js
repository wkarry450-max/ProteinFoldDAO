// ProteinFoldDAO 智能合约部署脚本
// 使用 Hardhat 或 Remix IDE 部署到 Sepolia 测试网

const { ethers } = require("hardhat");

async function main() {
    console.log("🚀 开始部署 ProteinFoldDAO 智能合约...");
    
    // 获取部署者账户
    const [deployer] = await ethers.getSigners();
    console.log("📝 部署账户:", deployer.address);
    
    // 检查账户余额
    const balance = await deployer.getBalance();
    console.log("💰 账户余额:", ethers.utils.formatEther(balance), "ETH");
    
    if (balance.lt(ethers.utils.parseEther("0.01"))) {
        console.log("⚠️  余额不足，请获取测试网ETH");
        console.log("🔗 Sepolia Faucet: https://sepoliafaucet.com/");
        return;
    }
    
    // 部署合约
    console.log("📦 正在部署合约...");
    const ProteinFoldingDAO = await ethers.getContractFactory("ProteinFoldingDAO");
    const dao = await ProteinFoldingDAO.deploy();
    
    await dao.deployed();
    
    console.log("✅ 合约部署成功!");
    console.log("📍 合约地址:", dao.address);
    console.log("🔗 交易哈希:", dao.deployTransaction.hash);
    
    // 验证部署
    console.log("\n🔍 验证部署...");
    const stats = await dao.getStats();
    console.log("📊 初始统计:", {
        totalPredictions: stats.totalPredictions.toString(),
        totalVotes: stats.totalVotes.toString()
    });
    
    // 保存部署信息
    const deploymentInfo = {
        network: "sepolia",
        contractAddress: dao.address,
        deployer: deployer.address,
        transactionHash: dao.deployTransaction.hash,
        blockNumber: dao.deployTransaction.blockNumber,
        timestamp: new Date().toISOString()
    };
    
    const fs = require('fs');
    fs.writeFileSync(
        'deployment.json', 
        JSON.stringify(deploymentInfo, null, 2)
    );
    
    console.log("💾 部署信息已保存到 deployment.json");
    
    // 输出前端配置
    console.log("\n🎨 前端配置信息:");
    console.log("CONTRACT_ADDRESS=" + dao.address);
    console.log("NETWORK_ID=11155111"); // Sepolia network ID
    console.log("RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID");
    
    console.log("\n🎉 部署完成! 现在可以在前端使用此合约地址。");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("❌ 部署失败:", error);
        process.exit(1);
    });

