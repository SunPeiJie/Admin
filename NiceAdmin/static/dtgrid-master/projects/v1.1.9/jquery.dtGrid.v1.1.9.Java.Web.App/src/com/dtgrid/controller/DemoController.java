package com.dtgrid.controller;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.collections.MapUtils;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

import com.dtgrid.model.Pager;
import com.dtgrid.utils.DtGridUtils;
import com.dtgrid.utils.PagerPropertyUtils;

/**
 * 演示
 * @author 大连首闻科技有限公司
 * @version 1.0
 */
@Controller
@RequestMapping("/dtgrid/demo")
public class DemoController {
	
	private JdbcTemplate jdbcTemplate;
	
	public JdbcTemplate getJdbcTemplate() {
		return jdbcTemplate;
	}

	@Resource(name="defaultJdbcTemplate")
	public void setJdbcTemplate(JdbcTemplate jdbcTemplate) {
		this.jdbcTemplate = jdbcTemplate;
	}

	/**
	 * 数据初始化
	 * @throws Exception
	 */
	@RequestMapping(value="/datas/init", method=RequestMethod.GET)
	public void initDatas(HttpServletResponse response) throws Exception {
//		格式化日期
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
		SimpleDateFormat timeFormat = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
//		插入初始数据
		StringBuffer sql = new StringBuffer();
		sql.append("insert into user (user_id, user_code, user_name, sex, salary, degree, time, time_stamp_s, time_stamp_ms, string_date, string_time) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
		List<Object[]> datas = new ArrayList<Object[]>();
		for(int i=0; i<200; i++){
			List<Object> data = new ArrayList<Object>();
			int id = (int)(Math.random()*1000)+10000;
			data.add("user_"+i);
			data.add("user_"+id);
			data.add("User No. "+id);
			data.add((int)((Math.random()*2)+1));
			data.add(Math.floor(Math.random()*6000+6000));
			data.add((int)((Math.random()*8)+1));
			data.add(new Date((long)Math.floor(Math.random()*1096588800000l)+(315504000000l)));
			data.add((Math.floor(Math.random()*1096588800000l)+315504000000l)/1000);
			data.add((Math.floor(Math.random()*1096588800000l)+315504000000l));
			data.add(dateFormat.format(new Date((long)Math.floor(Math.random()*1096588800000l)+(315504000000l))));
			data.add(timeFormat.format(new Date((long)Math.floor(Math.random()*1096588800000l)+(315504000000l))));
			datas.add(data.toArray());
		}
		jdbcTemplate.batchUpdate(sql.toString(), datas);
//		提示成功
		response.setCharacterEncoding("UTF-8");
		response.setContentType("text/html;charset=UTF-8");
		response.getWriter().write("数据初始化成功，共初始化 "+datas.size()+" 条数据。");
	}
	
	/**
	 * ajax分页动态加载模式
	 * @param dtGridPager Pager对象
	 * @param request 请求对象
	 * @param response 响应对象
	 * @throws Exception
	 */
	@RequestMapping(value="/datas/ajax", method=RequestMethod.POST)
	public void ajaxDatas(String dtGridPager, HttpServletRequest request, HttpServletResponse response) throws Exception {
//		映射Pager对象
		Pager pager = PagerPropertyUtils.copy(JSONObject.fromObject(dtGridPager));
//		获取SQL
		StringBuffer sql = new StringBuffer();
		sql.append("select * from user u where 1=1 ");
//		定义参数列表
		List<Object> args = new ArrayList<Object>();
//		判断是否包含自定义参数
		Map<String, Object> parameters = pager.getParameters();
		if(parameters.containsKey("like_user_code_or_user_name")){
			String like_user_code_or_user_name = MapUtils.getString(parameters, "like_user_code_or_user_name");
			if(like_user_code_or_user_name!=null&&!"".equals(like_user_code_or_user_name.trim())){
				sql.append("and u.user_code like ? or u.user_name like ? ");
				args.add("%"+like_user_code_or_user_name+"%");
				args.add("%"+like_user_code_or_user_name+"%");
			}
		}
//		执行查询
		DtGridUtils.queryForDTGrid(jdbcTemplate, sql.toString(), pager, request, response, args.toArray());
	}
	
	/**
	 * ajax全部加载模式
	 * @param dtGridPager Pager对象
	 * @param request 请求对象
	 * @param response 响应对象
	 * @throws Exception
	 */
	@RequestMapping(value="/datas/load_all", method=RequestMethod.POST)
	public void loadAll(HttpServletRequest request, HttpServletResponse response) throws Exception {
//		格式化日期
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
		SimpleDateFormat timeFormat = new SimpleDateFormat("yyyy-MM-dd hh:mm:ss");
//		模拟用户数据
		List<Map<String, Object>> userList = new ArrayList<Map<String,Object>>();
		for(int i=0; i<186; i++){
			Map<String, Object> user = new HashMap<String, Object>();
			user.put("user_id", "user_"+i);
			user.put("user_code", "user_"+i);
			user.put("user_name", "User No. "+(int)((Math.random()*1000)+10000));
			user.put("sex", (int)(Math.random()*2)+1);
			user.put("salary", (int)(Math.random()*6000)+6000);
			user.put("degree", (int)(Math.random()*8)+1);
			user.put("time", new Date((long)Math.floor(Math.random()*1096588800000l)+(315504000000l)));
			user.put("time_stamp_s", (Math.floor(Math.random()*1096588800000l)+315504000000l)/1000);
			user.put("time_stamp_ms", (Math.floor(Math.random()*1096588800000l)+315504000000l));
			user.put("string_date", dateFormat.format(new Date((long)Math.floor(Math.random()*1096588800000l)+(315504000000l))));
			user.put("string_time", timeFormat.format(new Date((long)Math.floor(Math.random()*1096588800000l)+(315504000000l))));
			userList.add(user);
		}
//		转换为JSON数据格式
		JSONArray userDatas = JSONArray.fromObject(userList);
//		回写数据
		response.setCharacterEncoding("UTF-8");
		response.setContentType("text/html;charset=UTF-8");
		response.getWriter().write(userDatas.toString());
	}
	
}